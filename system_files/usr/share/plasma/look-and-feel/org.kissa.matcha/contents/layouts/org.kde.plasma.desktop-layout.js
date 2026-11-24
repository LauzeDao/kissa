// kissa – Panel-Layout: Seitenleiste links + Notch oben
var desktops = desktopsForActivity(currentActivity());
for (var i = 0; i < desktops.length; i++) {
    desktops[i].wallpaperPlugin = "org.kde.image";
}

function set(panel, key, value) {
    try { panel[key] = value; } catch (e) { print("kissa: " + key + " nicht gesetzt: " + e); }
}

// ---------- Seitenleiste (Dock) links ----------
var dock = new Panel;
dock.location = "left";
dock.height = 60;                 // Dicke der Leiste
set(dock, "floating", true);
set(dock, "lengthMode", "fit");   // so lang wie der Inhalt
dock.alignment = "center";
dock.hiding = "none";

var launcher = dock.addWidget("org.kde.plasma.kickoff");
launcher.currentConfigGroup = ["General"];
launcher.writeConfig("icon", "/usr/share/kissa/hoji-launcher.png");

var tasks = dock.addWidget("org.kde.plasma.icontasks");
tasks.currentConfigGroup = ["General"];
tasks.writeConfig("launchers", [
    "applications:org.kde.dolphin.desktop",
    "preferred://browser",
    "applications:org.kde.konsole.desktop",
    "applications:org.kde.discover.desktop",
    "applications:systemsettings.desktop"
].join(","));

// ---------- Notch oben mittig ----------
var notch = new Panel;
notch.location = "top";
notch.height = 34;
set(notch, "floating", true);
set(notch, "lengthMode", "fit");
notch.alignment = "center";
notch.hiding = "none";

notch.addWidget("org.kde.plasma.systemtray");
var clock = notch.addWidget("org.kde.plasma.digitalclock");
clock.currentConfigGroup = ["Appearance"];
clock.writeConfig("showDate", "true");
clock.writeConfig("dateFormat", "shortDate");
