import QtQuick

// kissa – Ladebildschirm nach dem Login: Hoji wippt, darunter der Schriftzug.
Rectangle {
    id: root
    color: "#FAF4ED"
    property int stage

    Image {
        id: hoji
        source: "images/hoji.png"
        anchors.centerIn: parent
        anchors.verticalCenterOffset: -30
        height: 240
        fillMode: Image.PreserveAspectFit
        smooth: true
        transform: Translate { id: bob; y: 0 }
    }

    SequentialAnimation {
        running: true
        loops: Animation.Infinite
        NumberAnimation { target: bob; property: "y"; to: -10; duration: 650; easing.type: Easing.InOutQuad }
        NumberAnimation { target: bob; property: "y"; to: 0; duration: 650; easing.type: Easing.InOutQuad }
    }

    Text {
        text: "おかえり · kissa"
        color: "#575279"
        opacity: 0.85
        font.pixelSize: 22
        font.letterSpacing: 3
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: hoji.bottom
        anchors.topMargin: 28
    }

    Row {
        spacing: 10
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: hoji.bottom
        anchors.topMargin: 72
        Repeater {
            model: 5
            Rectangle {
                width: 10; height: 10; radius: 5
                color: "#7A9A4F"
                opacity: index < root.stage ? 1.0 : 0.25
                Behavior on opacity { NumberAnimation { duration: 200 } }
            }
        }
    }
}
