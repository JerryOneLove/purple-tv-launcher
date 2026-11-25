import os

c = chr(58)
n = chr(110) + chr(97) + chr(109) + chr(101)
a = "andr" + "oid"
os.makedirs("app/src/main/java/com/my/purplelauncher", exist_ok=True)

open("settings.gradle", "w").write(
    'pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }\n'
    'dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { google(); mavenCentral() } }\n'
    'rootProject.' + n + ' = "PurpleTVLauncher"\ninclude ":app"\n'
)

open("build.gradle", "w").write(
    f'plugins {{ id "com.{a}.application" version "8.2.2" apply false; id "org.jetbrains.kotlin.{a}" version "1.9.22" apply false }}\n'
)

open("gradle.properties", "w").write(
    f'org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8\n{a}.useAndroidX=true\n'
)

open("app/build.gradle", "w").write(
    f'plugins {{ id "com.{a}.application"; id "org.jetbrains.kotlin.{a}" }}\n'
    f'{a} {{ {n}space "com.my.purplelauncher"; compileSdk 34; defaultConfig {{ applicationId "com.my.purplelauncher"; minSdk 21; targetSdk 34; versionCode 3; versionName "3.0" }}; compileOptions {{ sourceCompatibility JavaVersion.VERSION_17; targetCompatibility JavaVersion.VERSION_17 }}; kotlinOptions {{ jvmTarget = "17" }} }}\n'
    'dependencies { implementation "androidx.appcompat:appcompat:1.6.1" }\n'
)

pkgs = [
    "llc.itdev.incy",
    "com.google.android.youtube.tv",
    "ru.kinopoisk.tv",
    "com.vk.tv",
    "ru.rutube.app",
    "tv.okko.androidtv",
    "ru.rt.video.app.tv",
    "ru.wink.androidtv",
    "com.yandex.browser.tv"
]
q_xml = "\n".join([f'        <package {a}{c}{n}="{p}" />' for p in pkgs])

manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns{c}{a}="http://schemas.{a}.com/apk/res/{a}">
    <uses-permission {a}{c}{n}="android.permission.READ_EXTERNAL_STORAGE" />
    <uses-permission {a}{c}{n}="android.permission.READ_MEDIA_IMAGES" />
    <uses-permission {a}{c}{n}="android.permission.QUERY_ALL_PACKAGES" />
    <queries>
{q_xml}
    </queries>
    <application {a}{c}allowBackup="false" {a}{c}label="Purple TV" {a}{c}theme="@style/Theme.AppCompat.NoActionBar">
        <activity {a}{c}{n}=".MainActivity" {a}{c}exported="true" {a}{c}launchMode="singleTask">
            <intent-filter>
                <action {a}{c}{n}="android.intent.action.MAIN" />
                <category {a}{c}{n}="android.intent.category.HOME" />
                <category {a}{c}{n}="android.intent.category.DEFAULT" />
                <category {a}{c}{n}="android.intent.category.LEANBACK_LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
open("app/src/main/AndroidManifest.xml", "w").write(manifest)

kt = """package com.my.purplelauncher

import android.Manifest
import android.app.AlertDialog
import android.content.Intent
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.graphics.BitmapFactory
import android.graphics.Color
import android.graphics.ColorMatrix
import android.graphics.ColorMatrixColorFilter
import android.graphics.drawable.BitmapDrawable
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.view.Gravity
import android.view.KeyEvent
import android.view.View
import android.view.WindowManager
import android.widget.FrameLayout
import android.widget.HorizontalScrollView
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.RelativeLayout
import android.widget.TextClock
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.io.File

class MainActivity : AppCompatActivity() {

    private val neonPurple = Color.parseColor("#C57BFF")
    private val idleGlass = Color.parseColor("#781A1826")
    private val focusGlass = Color.parseColor("#B52D2245")
    private val textLight = Color.parseColor("#F2EEFF")
    private val textSilver = Color.parseColor("#B8B4C7")

    private lateinit var uiOverlay: RelativeLayout
    private lateinit var bgView: ImageView
    private val idleHandler = Handler(Looper.getMainLooper())
    private var isScreensaver = false
    private val idleTimeoutMs = 20L * 60L * 1000L

    private val silverFilter by lazy {
        val cm = ColorMatrix().apply { setSaturation(0.08f) }
        val contrast = ColorMatrix(floatArrayOf(
            1.15f, 0f, 0f, 0f, 12f,
            0f, 1.15f, 0f, 0f, 12f,
            0f, 0f, 1.22f, 0f, 18f,
            0f, 0f, 0f, 1f, 0f
        ))
        cm.postConcat(contrast)
        ColorMatrixColorFilter(cm)
    }

    private val focusTintFilter by lazy {
        val cm = ColorMatrix().apply { setSaturation(0.45f) }
        val violetBoost = ColorMatrix(floatArrayOf(
            1.08f, 0f, 0f, 0f, 10f,
            0f, 1.00f, 0f, 0f, 4f,
            0f, 0f, 1.25f, 0f, 22f,
            0f, 0f, 0f, 1f, 0f
        ))
        cm.postConcat(violetBoost)
        ColorMatrixColorFilter(cm)
    }

    private val idleRunnable = Runnable {
        isScreensaver = true
        uiOverlay.animate().alpha(0f).setDuration(800).start()
    }

    data class AppSlot(val title: String, val packages: Array<String>)

    private val mainApps = arrayOf(
        AppSlot("YouTube", arrayOf("com.google.android.youtube.tv")),
        AppSlot("Кинопоиск", arrayOf("ru.kinopoisk.tv")),
        AppSlot("VK Видео", arrayOf("com.vk.tv")),
        AppSlot("Wink", arrayOf("ru.rt.video.app.tv", "ru.wink.androidtv", "ru.rt.wink")),
        AppSlot("Rutube", arrayOf("ru.rutube.app")),
        AppSlot("Okko", arrayOf("tv.okko.androidtv")),
        AppSlot("Браузер", arrayOf("com.yandex.browser.tv"))
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        val root = FrameLayout(this)
        bgView = ImageView(this).apply {
            scaleType = ImageView.ScaleType.CENTER_CROP
            layoutParams = FrameLayout.LayoutParams(-1, -1)
        }
        loadWallpaper(bgView)
        root.addView(bgView)

        uiOverlay = RelativeLayout(this).apply {
            layoutParams = FrameLayout.LayoutParams(-1, -1)
            setPadding(48, 32, 48, 24)
        }

        val clock = TextClock(this).apply {
            format24Hour = "HH:mm"
            textSize = 40f
            setTextColor(textLight)
            layoutParams = RelativeLayout.LayoutParams(-2, -2).apply {
                addRule(RelativeLayout.CENTER_HORIZONTAL)
                topMargin = 16
            }
        }
        uiOverlay.addView(clock)

        val topRight = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            layoutParams = RelativeLayout.LayoutParams(-2, -2).apply {
                addRule(RelativeLayout.ALIGN_PARENT_END)
                addRule(RelativeLayout.ALIGN_PARENT_TOP)
            }
        }

        val vpnBtn = createRoundBtn("VPN", true) { launchFirstFound(arrayOf("llc.itdev.incy")) }
        val wifiBtn = createRoundBtn("Wi-Fi", false) { openSettingsSafe(Settings.ACTION_WIFI_SETTINGS) }
        val cfgBtn = createRoundBtn("⚙", false) { openSettingsSafe(Settings.ACTION_SETTINGS) }
        val sleepBtn = createRoundBtn("☾", false) {
            isScreensaver = true
            uiOverlay.animate().alpha(0f).setDuration(500).start()
        }

        topRight.addView(vpnBtn)
        topRight.addView(wifiBtn)
        topRight.addView(cfgBtn)
        topRight.addView(sleepBtn)
        uiOverlay.addView(topRight)

        val bottomScroll = HorizontalScrollView(this).apply {
            isHorizontalScrollBarEnabled = false
            clipToPadding = false
            setPadding(8, 16, 8, 6)
            layoutParams = RelativeLayout.LayoutParams(-1, -2).apply {
                addRule(RelativeLayout.ALIGN_PARENT_BOTTOM)
            }
        }

        val dock = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_HORIZONTAL
        }

        var firstTile: View? = null
        for (slot in mainApps) {
            val tile = createAppTile(slot)
            if (firstTile == null) firstTile = tile
            dock.addView(tile)
        }

        val allAppsTile = createSpecialTile("Все") { showAllAppsDialog() }
        dock.addView(allAppsTile)

        bottomScroll.addView(dock)
        uiOverlay.addView(bottomScroll)
        root.addView(uiOverlay)
        setContentView(root)

        if (Build.VERSION.SDK_INT >= 23) {
            val perm = if (Build.VERSION.SDK_INT >= 33) Manifest.permission.READ_MEDIA_IMAGES else Manifest.permission.READ_EXTERNAL_STORAGE
            if (checkSelfPermission(perm) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(arrayOf(perm), 101)
            }
        }

        firstTile?.post { firstTile.requestFocus() }
        resetIdleTimer()
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        loadWallpaper(bgView)
    }

    private fun loadWallpaper(iv: ImageView) {
        val candidates = arrayOf(
            File("/sdcard/Download/bg.png"),
            File("/sdcard/Download/bg.jpg"),
            File("/storage/emulated/0/Download/bg.png"),
            File("/storage/emulated/0/Download/bg.jpg")
        )
        for (f in candidates) {
            if (f.exists() && f.canRead()) {
                val bmp = BitmapFactory.decodeFile(f.absolutePath)
                if (bmp != null) {
                    iv.setImageDrawable(BitmapDrawable(resources, bmp))
                    return
                }
            }
        }
iv.setImageDrawable(GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(Color.parseColor("#181326"), Color.parseColor("#2E1D47"))))
}
private fun createRoundBtn(label: String, accent: Boolean, onClick: () -> Unit): TextView {
return TextView(this).apply {
text = label
textSize = if (label.length > 2) 13f else 17f
setTextColor(if (accent) textLight else textSilver)
gravity = Gravity.CENTER
isFocusable = true
layoutParams = LinearLayout.LayoutParams(68, 68).apply { leftMargin = 14 }
background = roundBg(false, accent)
setOnFocusChangeListener { v, f ->
v.background = roundBg(f, accent)
(v as TextView).setTextColor(if (f || accent) textLight else textSilver)
v.animate().scaleX(if (f) 1.12f else 1f).scaleY(if (f) 1.12f else 1f).setDuration(120).start()
}
setOnClickListener { onClick() }
}
}
private fun roundBg(focused: Boolean, accent: Boolean) = GradientDrawable().apply {
shape = GradientDrawable.OVAL
setColor(if (focused) focusGlass else if (accent) Color.parseColor("#883C2866") else idleGlass)
setStroke(if (focused) 5 else 2, if (focused || accent) neonPurple else Color.parseColor("#55A799FF"))
}
private fun createAppTile(slot: AppSlot): LinearLayout {
val box = LinearLayout(this).apply {
orientation = LinearLayout.VERTICAL
gravity = Gravity.CENTER
isFocusable = true
setPadding(12, 12, 12, 10)
layoutParams = LinearLayout.LayoutParams(156, 132).apply { setMargins(10, 6, 10, 6) }
background = tileBg(false)
}
val iconView = ImageView(this).apply {
scaleType = ImageView.ScaleType.FIT_CENTER
layoutParams = LinearLayout.LayoutParams(116, 68)
colorFilter = silverFilter
}
val foundPkg = slot.packages.firstOrNull { isInstalled(it) }
if (foundPkg != null) {
val drawable = try {
packageManager.getApplicationBanner(foundPkg) ?: packageManager.getApplicationIcon(foundPkg)
} catch (e: Exception) {
null
}
if (drawable != null) iconView.setImageDrawable(drawable)
} else {
iconView.setImageResource(android.R.drawable.ic_menu_view)
iconView.alpha = 0.55f
}
val titleView = TextView(this).apply {
text = slot.title
textSize = 13f
setTextColor(textSilver)
gravity = Gravity.CENTER
maxLines = 1
layoutParams = LinearLayout.LayoutParams(-1, -2).apply { topMargin = 6 }
}
box.addView(iconView)
box.addView(titleView)
box.setOnFocusChangeListener { v, f ->
v.background = tileBg(f)
iconView.colorFilter = if (f) focusTintFilter else silverFilter
titleView.setTextColor(if (f) textLight else textSilver)
v.animate().scaleX(if (f) 1.10f else 1f).scaleY(if (f) 1.10f else 1f).setDuration(120).start()
}
box.setOnClickListener { launchFirstFound(slot.packages) }
return box
}
private fun createSpecialTile(label: String, onClick: () -> Unit): LinearLayout {
val box = LinearLayout(this).apply {
orientation = LinearLayout.VERTICAL
gravity = Gravity.CENTER
isFocusable = true
layoutParams = LinearLayout.LayoutParams(112, 132).apply { setMargins(10, 6, 10, 6) }
background = tileBg(false)
}
val plus = TextView(this).apply {
text = "⋮⋮"
textSize = 26f
setTextColor(textSilver)
gravity = Gravity.CENTER
}
val title = TextView(this).apply {
text = label
textSize = 13f
setTextColor(textSilver)
gravity = Gravity.CENTER
layoutParams = LinearLayout.LayoutParams(-1, -2).apply { topMargin = 6 }
}
box.addView(plus)
box.addView(title)
box.setOnFocusChangeListener { v, f ->
v.background = tileBg(f)
plus.setTextColor(if (f) neonPurple else textSilver)
title.setTextColor(if (f) textLight else textSilver)
v.animate().scaleX(if (f) 1.10f else 1f).scaleY(if (f) 1.10f else 1f).setDuration(120).start()
}
box.setOnClickListener { onClick() }
return box
}
private fun tileBg(focused: Boolean) = GradientDrawable().apply {
cornerRadius = 20f
setColor(if (focused) focusGlass else idleGlass)
setStroke(if (focused) 5 else 1, if (focused) neonPurple else Color.parseColor("#38FFFFFF"))
}
private fun isInstalled(pkg: String): Boolean {
return try {
packageManager.getPackageInfo(pkg, 0)
true
} catch (e: Exception) {
false
}
}
private fun launchFirstFound(pkgs: Array) {
for (p in pkgs) {
val intent = packageManager.getLeanbackLaunchIntentForPackage(p) ?: packageManager.getLaunchIntentForPackage(p)
if (intent != null) {
startActivity(intent)
return
}
}
Toast.makeText(this, "Приложение ещё не установлено", Toast.LENGTH_SHORT).show()
}
private fun openSettingsSafe(action: String) {
try {
startActivity(Intent(action))
} catch (e: Exception) {
startActivity(Intent(Settings.ACTION_SETTINGS))
}
}
private fun showAllAppsDialog() {
val rawList = packageManager.getInstalledApplications(0)
val launchable = mutableListOf()
for (info in rawList) {
if (packageManager.getLeanbackLaunchIntentForPackage(info.packageName) != null ||
packageManager.getLaunchIntentForPackage(info.packageName) != null) {
launchable.add(info)
}
}
launchable.sortWith(Comparator { o1, o2 ->
packageManager.getApplicationLabel(o1).toString().compareTo(packageManager.getApplicationLabel(o2).toString())
})
val names = Array(launchable.size) { idx -> packageManager.getApplicationLabel(launchable[idx]).toString() }
AlertDialog.Builder(this)
.setTitle("Все приложения")
.setItems(names) { _, idx -> launchFirstFound(arrayOf(launchable[idx].packageName)) }
.show()
}
private fun resetIdleTimer() {
idleHandler.removeCallbacks(idleRunnable)
if (isScreensaver) {
isScreensaver = false
uiOverlay.animate().alpha(1f).setDuration(300).start()
}
idleHandler.postDelayed(idleRunnable, idleTimeoutMs)
}
override fun dispatchKeyEvent(event: KeyEvent): Boolean {
if (event.action == KeyEvent.ACTION_DOWN) {
if (isScreensaver) {
resetIdleTimer()
return true
}
resetIdleTimer()
}
return super.dispatchKeyEvent(event)
}
override fun onResume() {
super.onResume()
resetIdleTimer()
}
@Suppress("DEPRECATION")
override fun onBackPressed() {
if (isScreensaver) resetIdleTimer()
}
}
"""
open("app/src/main/java/com/my/purplelauncher/MainActivity.kt", "w").write(kt)
