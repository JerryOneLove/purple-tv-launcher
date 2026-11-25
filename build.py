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
    f'{a} {{ {n}space "com.my.purplelauncher"; compileSdk 34; defaultConfig {{ applicationId "com.my.purplelauncher"; minSdk 21; targetSdk 34; versionCode 1; versionName "1.0" }}; compileOptions {{ sourceCompatibility JavaVersion.VERSION_17; targetCompatibility JavaVersion.VERSION_17 }}; kotlinOptions {{ jvmTarget = "17" }} }}\n'
    'dependencies { implementation "androidx.appcompat:appcompat:1.6.1" }\n'
)

pkgs = ["llc.itdev.incy", "com.google.android.youtube.tv", "ru.kinopoisk.tv", "com.vk.tv", "ru.rutube.app", "tv.okko.androidtv", "com.yandex.browser.tv"]
q_xml = "\n".join([f'        <package {a}{c}{n}="{p}" />' for p in pkgs])

manifest = f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns{c}{a}="http://schemas.{a}.com/apk/res/{a}">
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
import android.content.Intent
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    private val bgDark = Color.parseColor("#1C1B22")
    private val cardGray = Color.parseColor("#2B2936")
    private val cardFocused = Color.parseColor("#453E5C")
    private val accentPurple = Color.parseColor("#A799FF")
    private val textMain = Color.parseColor("#EAE6F5")
    private val apps = listOf(
        "YouTube" to "com.google.android.youtube.tv",
        "Кинопоиск" to "ru.kinopoisk.tv",
        "VK Видео" to "com.vk.tv",
        "Rutube" to "ru.rutube.app",
        "Okko" to "tv.okko.androidtv",
        "Браузер" to "com.yandex.browser.tv"
    )
    override fun onCreate(s: Bundle?) {
        super.onCreate(s)
        val root = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setBackgroundColor(bgDark); setPadding(64, 48, 64, 48) }
        val top = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        val vpn = tile("VPN (INCY)", true) { openApp("llc.itdev.incy") }.apply { layoutParams = LinearLayout.LayoutParams(0, 130, 1f).apply { rightMargin = 24 } }
        val cfg = tile("Настройки", false) { startActivity(Intent(Settings.ACTION_SETTINGS)) }.apply { layoutParams = LinearLayout.LayoutParams(320, 130).apply { rightMargin = 32 } }
        val clk = TextClock(this).apply { format24Hour = "HH:mm"; textSize = 36f; setTextColor(textMain) }
        top.addView(vpn); top.addView(cfg); top.addView(clk); root.addView(top)
        val grid = GridLayout(this).apply { columnCount = 3; layoutParams = LinearLayout.LayoutParams(-1, -2).apply { topMargin = 48 } }
        for ((t, p) in apps) {
            grid.addView(tile(t, false) { openApp(p) }.apply {
                layoutParams = GridLayout.LayoutParams().apply { width = 0; height = 200; columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f); setMargins(12, 12, 12, 12) }
            })
        }
        root.addView(grid); setContentView(root); vpn.requestFocus()
    }
    private fun tile(lbl: String, acc: Boolean, click: () -> Unit) = TextView(this).apply {
        text = lbl; textSize = if (acc) 22f else 24f; setTextColor(textMain); gravity = Gravity.CENTER; isFocusable = true; background = bg(false, acc)
        setOnFocusChangeListener { v, f -> v.background = bg(f, acc); v.animate().scaleX(if (f) 1.04f else 1f).scaleY(if (f) 1.04f else 1f).setDuration(120).start() }
        setOnClickListener { click() }
    }
    private fun bg(f: Boolean, acc: Boolean) = GradientDrawable().apply {
        cornerRadius = 24f
        setColor(if (f) cardFocused else if (acc) Color.parseColor("#3B3354") else cardGray)
        setStroke(if (f) 5 else 2, if (f || acc) accentPurple else Color.parseColor("#3F3D4D"))
    }
    private fun openApp(p: String) {
        val i = packageManager.getLeanbackLaunchIntentForPackage(p) ?: packageManager.getLaunchIntentForPackage(p)
        if (i != null) startActivity(i) else Toast.makeText(this, "Не найдено: $p", Toast.LENGTH_SHORT).show()
    }
    override fun onBackPressed() {}
}
"""
open("app/src/main/java/com/my/purplelauncher/MainActivity.kt", "w").write(kt)
