import os

c = chr(58)
n = chr(110) + chr(97) + chr(109) + chr(101)
a = "andr" + "oid"
lt = chr(60)
gt = chr(62)
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
    f'{a} {{ {n}space "com.my.purplelauncher"; compileSdk 34; defaultConfig {{ applicationId "com.my.purplelauncher"; minSdk 21; targetSdk 34; versionCode 4; versionName "4.0" }}; compileOptions {{ sourceCompatibility JavaVersion.VERSION_17; targetCompatibility JavaVersion.VERSION_17 }}; kotlinOptions {{ jvmTarget = "17" }} }}\n'
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
q_xml = "\n".join([f'        {lt}package {a}{c}{n}="{p}" /{gt}' for p in pkgs])

manifest = f"""{lt}?xml version="1.0" encoding="utf-8"?{gt}
{lt}manifest xmlns{c}{a}="http://schemas.{a}.com/apk/res/{a}"{gt}
    {lt}uses-permission {a}{c}{n}="android.permission.READ_EXTERNAL_STORAGE" /{gt}
    {lt}uses-permission {a}{c}{n}="android.permission.READ_MEDIA_IMAGES" /{gt}
    {lt}uses-permission {a}{c}{n}="android.permission.QUERY_ALL_PACKAGES" /{gt}
    {lt}queries{gt}
{q_xml}
    {lt}/queries{gt}
    {lt}application {a}{c}allowBackup="false" {a}{c}label="Purple TV" {a}{c}theme="@style/Theme.AppCompat.NoActionBar"{gt}
        {lt}activity {a}{c}{n}=".MainActivity" {a}{c}exported="true" {a}{c}launchMode="singleTask"{gt}
            {lt}intent-filter{gt}
                {lt}action {a}{c}{n}="android.intent.action.MAIN" /{gt}
                {lt}category {a}{c}{n}="android.intent.category.HOME" /{gt}
                {lt}category {a}{c}{n}="android.intent.category.DEFAULT" /{gt}
                {lt}category {a}{c}{n}="android.intent.category.LEANBACK_LAUNCHER" /{gt}
            {lt}/intent-filter{gt}
        {lt}/activity{gt}
    {lt}/application{gt}
{lt}/manifest{gt}
"""
open("app/src/main/AndroidManifest.xml", "w").write(manifest)

kt = f"""package com.my.purplelauncher

import android.Manifest
import android.app.AlertDialog
import android.content.Context
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

class MainActivity : AppCompatActivity() {{

    private val neonPurple = Color.parseColor("#C57BFF")
    private val idleGlass = Color.parseColor("#781A1826")
    private val focusGlass = Color.parseColor("#B52D2245")
    private val textLight = Color.parseColor("#F2EEFF")
    private val textSilver = Color.parseColor("#B8B4C7")

    private lateinit var uiOverlay: RelativeLayout
    private lateinit var bgView: ImageView
    private lateinit var dock: LinearLayout
    private val idleHandler = Handler(Looper.getMainLooper())
    private var isScreensaver = false
    private val idleTimeoutMs = 20L * 60L * 1000L

    private val prefs by lazy {{ getSharedPreferences("purple_tv_prefs", Context.MODE_PRIVATE) }}

    private val silverFilter by lazy {{
        val cm = ColorMatrix().apply {{ setSaturation(0.08f) }}
        val contrast = ColorMatrix(floatArrayOf(
            1.15f, 0f, 0f, 0f, 12f,
            0f, 1.15f, 0f, 0f, 12f,
            0f, 0f, 1.22f, 0f, 18f,
            0f, 0f, 0f, 1f, 0f
        ))
        cm.postConcat(contrast)
        ColorMatrixColorFilter(cm)
    }}

    private val focusTintFilter by lazy {{
        val cm = ColorMatrix().apply {{ setSaturation(0.45f) }}
        val violetBoost = ColorMatrix(floatArrayOf(
            1.08f, 0f, 0f, 0f, 10f,
            0f, 1.00f, 0f, 0f, 4f,
            0f, 0f, 1.25f, 0f, 22f,
            0f, 0f, 0f, 1f, 0f
        ))
        cm.postConcat(violetBoost)
        ColorMatrixColorFilter(cm)
    }}

    private val idleRunnable = Runnable {{
        isScreensaver = true
        uiOverlay.animate().alpha(0f).setDuration(800).start()
    }}

    data class AppSlot(val title: String, val packages: Array{lt}String{gt}, val isCustom: Boolean = false)

    private val defaultSlots = arrayOf(
        AppSlot("YouTube", arrayOf("com.google.android.youtube.tv")),
        AppSlot("Кинопоиск", arrayOf("ru.kinopoisk.tv")),
        AppSlot("VK Видео", arrayOf("com.vk.tv")),
        AppSlot("Wink", arrayOf("ru.rt.video.app.tv", "ru.wink.androidtv", "ru.rt.wink")),
        AppSlot("Rutube", arrayOf("ru.rutube.app")),
        AppSlot("Okko", arrayOf("tv.okko.androidtv")),
        AppSlot("Браузер", arrayOf("com.yandex.browser.tv"))
    )

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        val root = FrameLayout(this)
        bgView = ImageView(this).apply {{
            scaleType = ImageView.ScaleType.CENTER_CROP
            layoutParams = FrameLayout.LayoutParams(-1, -1)
        }}
        loadWallpaper(bgView)
        root.addView(bgView)

        uiOverlay = RelativeLayout(this).apply {{
            layoutParams = FrameLayout.LayoutParams(-1, -1)
            setPadding(48, 32, 48, 24)
        }}

        val clock = TextClock(this).apply {{
            format24Hour = "HH:mm"
            textSize = 40f
            setTextColor(textLight)
            layoutParams = RelativeLayout.LayoutParams(-2, -2).apply {{
                addRule(RelativeLayout.CENTER_HORIZONTAL)
                topMargin = 16
            }}
        }}
        uiOverlay.addView(clock)

        val topRight = LinearLayout(this).apply {{
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            layoutParams = RelativeLayout.LayoutParams(-2, -2).apply {{
                addRule(RelativeLayout.ALIGN_PARENT_END)
                addRule(RelativeLayout.ALIGN_PARENT_TOP)
            }}
        }}

        val vpnBtn = createRoundBtn("VPN", true) {{ launchFirstFound(arrayOf("llc.itdev.incy")) }}
        val wifiBtn = createRoundBtn("Wi-Fi", false) {{ openSettingsSafe(Settings.ACTION_WIFI_SETTINGS) }}
        val cfgBtn = createRoundBtn("⚙", false) {{ openSettingsSafe(Settings.ACTION_SETTINGS) }}
        val sleepBtn = createRoundBtn("☾", false) {{
            isScreensaver = true
            uiOverlay.animate().alpha(0f).setDuration(500).start()
        }}

        topRight.addView(vpnBtn)
        topRight.addView(wifiBtn)
        topRight.addView(cfgBtn)
        topRight.addView(sleepBtn)
        uiOverlay.addView(topRight)

        val bottomScroll = HorizontalScrollView(this).apply {{
            isHorizontalScrollBarEnabled = false
            clipToPadding = false
            setPadding(8, 16, 8, 6)
            layoutParams = RelativeLayout.LayoutParams(-1, -2).apply {{
                addRule(RelativeLayout.ALIGN_PARENT_BOTTOM)
            }}
        }}

        dock = LinearLayout(this).apply {{
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_HORIZONTAL
        }}

        rebuildDock()

        bottomScroll.addView(dock)
        uiOverlay.addView(bottomScroll)
        root.addView(uiOverlay)
        setContentView(root)

        if (Build.VERSION.SDK_INT {gt}= 23) {{
            val perm = if (Build.VERSION.SDK_INT {gt}= 33) Manifest.permission.READ_MEDIA_IMAGES else Manifest.permission.READ_EXTERNAL_STORAGE
            if (checkSelfPermission(perm) != PackageManager.PERMISSION_GRANTED) {{
                requestPermissions(arrayOf(perm), 101)
            }}
        }}

        resetIdleTimer()
    }}

    private fun getActiveSlots(): ArrayList{lt}AppSlot{gt} {{
        val hidden = prefs.getStringSet("hidden_titles", emptySet()) ?: emptySet()
        val customPkgs = prefs.getString("custom_pkgs", "") ?: ""
        val result = ArrayList{lt}AppSlot{gt}()
        for (slot in defaultSlots) {{
            if (!hidden.contains(slot.title)) {{
                result.add(slot)
            }}
        }}
        if (customPkgs.isNotEmpty()) {{
            for (pkg in customPkgs.split("|")) {{
                if (pkg.isNotEmpty() && isInstalled(pkg)) {{
                    val label = try {{
                        packageManager.getApplicationLabel(packageManager.getApplicationInfo(pkg, 0)).toString()
                    }} catch (e: Exception) {{ pkg }}
                    result.add(AppSlot(label, arrayOf(pkg), true))
                }}
}}
}}
return result
}}
private fun rebuildDock() {{
dock.removeAllViews()
var firstTile: View? = null
for (slot in getActiveSlots()) {{
val tile = createAppTile(slot)
if (firstTile == null) firstTile = tile
dock.addView(tile)
}}
val allAppsTile = createSpecialTile("Все") {{ showAllAppsDialog() }}
if (firstTile == null) firstTile = allAppsTile
dock.addView(allAppsTile)
firstTile.post {{ firstTile.requestFocus() }}
}}
private fun hideOrRemoveSlot(slot: AppSlot) {{
if (slot.isCustom) {{
val current = (prefs.getString("custom_pkgs", "") ?: "").split("|").filter {{ it.isNotEmpty() && it != slot.packages[0] }}
prefs.edit().putString("custom_pkgs", current.joinToString("|")).apply()
}} else {{
val hidden = HashSet{lt}String{gt}(prefs.getStringSet("hidden_titles", emptySet()) ?: emptySet())
hidden.add(slot.title)
prefs.edit().putStringSet("hidden_titles", hidden).apply()
}}
rebuildDock()
Toast.makeText(this, "Убрано с главного экрана", Toast.LENGTH_SHORT).show()
}}
private fun addCustomApp(pkg: String) {{
for (slot in defaultSlots) {{
if (slot.packages.contains(pkg)) {{
val hidden = HashSet{lt}String{gt}(prefs.getStringSet("hidden_titles", emptySet()) ?: emptySet())
if (hidden.remove(slot.title)) {{
prefs.edit().putStringSet("hidden_titles", hidden).apply()
rebuildDock()
Toast.makeText(this, "Возвращено на главный экран", Toast.LENGTH_SHORT).show()
}} else {{
Toast.makeText(this, "Уже есть на главном экране", Toast.LENGTH_SHORT).show()
}}
return
}}
}}
val current = ArrayList{lt}String{gt}((prefs.getString("custom_pkgs", "") ?: "").split("|").filter {{ it.isNotEmpty() }})
if (!current.contains(pkg)) {{
current.add(pkg)
prefs.edit().putString("custom_pkgs", current.joinToString("|")).apply()
rebuildDock()
Toast.makeText(this, "Добавлено на главный экран", Toast.LENGTH_SHORT).show()
}} else {{
Toast.makeText(this, "Уже есть на главном экране", Toast.LENGTH_SHORT).show()
}}
}}
override fun onRequestPermissionsResult(requestCode: Int, permissions: Array{lt}out String{gt}, grantResults: IntArray) {{
super.onRequestPermissionsResult(requestCode, permissions, grantResults)
loadWallpaper(bgView)
}}
private fun loadWallpaper(iv: ImageView) {{
val candidates = arrayOf(
File("/sdcard/Download/bg.png"),
File("/sdcard/Download/bg.jpg"),
File("/storage/emulated/0/Download/bg.png"),
File("/storage/emulated/0/Download/bg.jpg")
)
for (f in candidates) {{
if (f.exists() && f.canRead()) {{
val bmp = BitmapFactory.decodeFile(f.absolutePath)
if (bmp != null) {{
iv.setImageDrawable(BitmapDrawable(resources, bmp))
return
}}
}}
}}
iv.setImageDrawable(GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM, intArrayOf(Color.parseColor("#181326"), Color.parseColor("#2E1D47"))))
}}
private fun createRoundBtn(label: String, accent: Boolean, onClick: () -{gt} Unit): TextView {{
return TextView(this).apply {{
text = label
textSize = if (label.length {gt} 2) 13f else 17f
setTextColor(if (accent) textLight else textSilver)
gravity = Gravity.CENTER
isFocusable = true
layoutParams = LinearLayout.LayoutParams(68, 68).apply {{ leftMargin = 14 }}
background = roundBg(false, accent)
setOnFocusChangeListener {{ v, f -{gt}
v.background = roundBg(f, accent)
(v as TextView).setTextColor(if (f || accent) textLight else textSilver)
v.animate().scaleX(if (f) 1.12f else 1f).scaleY(if (f) 1.12f else 1f).setDuration(120).start()
}}
setOnClickListener {{ onClick() }}
}}
}}
private fun roundBg(focused: Boolean, accent: Boolean) = GradientDrawable().apply {{
shape = GradientDrawable.OVAL
setColor(if (focused) focusGlass else if (accent) Color.parseColor("#883C2866") else idleGlass)
setStroke(if (focused) 5 else 2, if (focused || accent) neonPurple else Color.parseColor("#55A799FF"))
}}
private fun createAppTile(slot: AppSlot): LinearLayout {{
val box = LinearLayout(this).apply {{
orientation = LinearLayout.VERTICAL
gravity = Gravity.CENTER
isFocusable = true
isLongClickable = true
setPadding(12, 12, 12, 10)
layoutParams = LinearLayout.LayoutParams(156, 132).apply {{ setMargins(10, 6, 10, 6) }}
background = tileBg(false)
}}
val iconView = ImageView(this).apply {{
scaleType = ImageView.ScaleType.FIT_CENTER
layoutParams = LinearLayout.LayoutParams(116, 68)
colorFilter = silverFilter
}}
val foundPkg = slot.packages.firstOrNull {{ isInstalled(it) }}
if (foundPkg != null) {{
val drawable = try {{
packageManager.getApplicationBanner(foundPkg) ?: packageManager.getApplicationIcon(foundPkg)
}} catch (e: Exception) {{
null
}}
if (drawable != null) iconView.setImageDrawable(drawable)
}} else {{
iconView.setImageResource(android.R.drawable.ic_menu_view)
iconView.alpha = 0.55f
}}
val titleView = TextView(this).apply {{
text = slot.title
textSize = 13f
setTextColor(textSilver)
gravity = Gravity.CENTER
maxLines = 1
layoutParams = LinearLayout.LayoutParams(-1, -2).apply {{ topMargin = 6 }}
}}
box.addView(iconView)
box.addView(titleView)
box.setOnFocusChangeListener {{ v, f -{gt}
v.background = tileBg(f)
iconView.colorFilter = if (f) focusTintFilter else silverFilter
titleView.setTextColor(if (f) textLight else textSilver)
v.animate().scaleX(if (f) 1.10f else 1f).scaleY(if (f) 1.10f else 1f).setDuration(120).start()
}}
box.setOnClickListener {{ launchFirstFound(slot.packages) }}
box.setOnLongClickListener {{
AlertDialog.Builder(this)
.setTitle(slot.title)
.setItems(arrayOf("Открыть", "Убрать с главного экрана")) {{ _, which -{gt}
if (which == 0) launchFirstFound(slot.packages) else hideOrRemoveSlot(slot)
}}
.show()
true
}}
return box
}}
private fun createSpecialTile(label: String, onClick: () -{gt} Unit): LinearLayout {{
val box = LinearLayout(this).apply {{
orientation = LinearLayout.VERTICAL
gravity = Gravity.CENTER
isFocusable = true
layoutParams = LinearLayout.LayoutParams(112, 132).apply {{ setMargins(10, 6, 10, 6) }}
background = tileBg(false)
}}
val plus = TextView(this).apply {{
text = "⋮⋮"
textSize = 26f
setTextColor(textSilver)
gravity = Gravity.CENTER
}}
val title = TextView(this).apply {{
text = label
textSize = 13f
setTextColor(textSilver)
gravity = Gravity.CENTER
layoutParams = LinearLayout.LayoutParams(-1, -2).apply {{ topMargin = 6 }}
}}
box.addView(plus)
box.addView(title)
box.setOnFocusChangeListener {{ v, f -{gt}
v.background = tileBg(f)
plus.setTextColor(if (f) neonPurple else textSilver)
title.setTextColor(if (f) textLight else textSilver)
v.animate().scaleX(if (f) 1.10f else 1f).scaleY(if (f) 1.10f else 1f).setDuration(120).start()
}}
box.setOnClickListener {{ onClick() }}
return box
}}
private fun tileBg(focused: Boolean) = GradientDrawable().apply {{
cornerRadius = 20f
setColor(if (focused) focusGlass else idleGlass)
setStroke(if (focused) 5 else 1, if (focused) neonPurple else Color.parseColor("#38FFFFFF"))
}}
private fun isInstalled(pkg: String): Boolean {{
return try {{
packageManager.getPackageInfo(pkg, 0)
true
}} catch (e: Exception) {{
false
}}
}}
private fun launchFirstFound(pkgs: Array{lt}String{gt}) {{
for (p in pkgs) {{
val intent = packageManager.getLeanbackLaunchIntentForPackage(p) ?: packageManager.getLaunchIntentForPackage(p)
if (intent != null) {{
startActivity(intent)
return
}}
}}
Toast.makeText(this, "Приложение ещё не установлено", Toast.LENGTH_SHORT).show()
}}
private fun openSettingsSafe(action: String) {{
try {{
startActivity(Intent(action))
}} catch (e: Exception) {{
startActivity(Intent(Settings.ACTION_SETTINGS))
}}
}}
private fun showAllAppsDialog() {{
val rawList = packageManager.getInstalledApplications(0)
val launchable = ArrayList{lt}ApplicationInfo{gt}()
for (info in rawList) {{
if (info.packageName != packageName &&
(packageManager.getLeanbackLaunchIntentForPackage(info.packageName) != null ||
packageManager.getLaunchIntentForPackage(info.packageName) != null)) {{
launchable.add(info)
}}
}}
launchable.sortWith(Comparator {{ o1, o2 -{gt}
packageManager.getApplicationLabel(o1).toString().compareTo(packageManager.getApplicationLabel(o2).toString())
}})
val names = Array(launchable.size + 1) {{ idx -{gt}
if (idx == launchable.size) "↺ Вернуть стандартный список" else packageManager.getApplicationLabel(launchable[idx]).toString()
}}
AlertDialog.Builder(this)
.setTitle("Все приложения (нажмите для выбора)")
.setItems(names) {{ _, idx -{gt}
if (idx == launchable.size) {{
prefs.edit().clear().apply()
rebuildDock()
Toast.makeText(this, "Список сброшен", Toast.LENGTH_SHORT).show()
}} else {{
val chosen = launchable[idx]
val appName = packageManager.getApplicationLabel(chosen).toString()
AlertDialog.Builder(this)
.setTitle(appName)
.setItems(arrayOf("Запустить", "Добавить на главный экран")) {{ _, actionIdx -{gt}
if (actionIdx == 0) launchFirstFound(arrayOf(chosen.packageName))
else addCustomApp(chosen.packageName)
}}
.show()
}}
}}
.show()
}}
private fun resetIdleTimer() {{
idleHandler.removeCallbacks(idleRunnable)
if (isScreensaver) {{
isScreensaver = false
uiOverlay.animate().alpha(1f).setDuration(300).start()
}}
idleHandler.postDelayed(idleRunnable, idleTimeoutMs)
}}
override fun dispatchKeyEvent(event: KeyEvent): Boolean {{
if (event.action == KeyEvent.ACTION_DOWN) {{
if (isScreensaver) {{
resetIdleTimer()
return true
}}
resetIdleTimer()
}}
return super.dispatchKeyEvent(event)
}}
override fun onResume() {{
super.onResume()
resetIdleTimer()
}}
@Suppress("DEPRECATION")
override fun onBackPressed() {{
if (isScreensaver) resetIdleTimer()
}}
}}
"""
open("app/src/main/java/com/my/purplelauncher/MainActivity.kt", "w").write(kt)
