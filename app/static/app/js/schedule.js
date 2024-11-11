// 最初に表示する日数（例えば、5日間分のタブを表示する場合）
const maxTabs = 10; // 最大タブ数（必要に応じて変更可能）
let tabCount = 5;  // ここで最初に表示する日数を指定

// ページ読み込み時にタブを復元
document.addEventListener("DOMContentLoaded", function() {
    // ここで指定された日数だけタブを作成
    for (let i = 1; i <= tabCount; i++) {
        createTab(i);
    }

    // 最初に作成したタブをデフォルトで開く
    document.getElementById("tab1").style.display = "block";
    document.getElementsByClassName("tablinks")[0].classList.add("active");
});

// タブを表示する関数
function openTab(evt, tabName) {
    const tabcontent = document.getElementsByClassName("tabcontent");
    const tablinks = document.getElementsByClassName("tablinks");

    // すべてのタブコンテンツを非表示にする
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // すべてのタブリンクからアクティブクラスを削除する
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }

    // 現在のタブコンテンツを表示し、アクティブクラスを追加する
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");
}

// 新しいタブを作成する関数
function createTab(day) {
    const newTabName = `tab${day}`;

    // すでにそのタブが存在する場合は何もしない
    if (document.getElementById(newTabName)) return;

    const newTabLabel = `${day}日目`;

    // 新しいタブボタンを作成
    const newTabButton = document.createElement("button");
    newTabButton.className = "tablinks";
    newTabButton.textContent = newTabLabel;
    newTabButton.setAttribute("onclick", `openTab(event, '${newTabName}')`);

    // 最初のタブだけ「defaultOpen」にする
    if (day === 1 && !document.getElementById("tab1")) {
        newTabButton.id = "defaultOpen";
    }

    // 2日目以降のタブに削除ボタンを追加
    if (day > 1) {
        const closeButton = document.createElement("span");
        closeButton.textContent = " ×";
        closeButton.style.cursor = "pointer";
        closeButton.style.marginLeft = "8px";
        closeButton.style.color = "red";
        closeButton.onclick = (event) => {
            event.stopPropagation(); // タブを開かないようにする
            removeTab(day);
        };
        newTabButton.appendChild(closeButton);
    }

    // 新しいタブコンテンツを作成
    const newTabContent = document.createElement("div");
    newTabContent.id = newTabName;
    newTabContent.className = "tabcontent";
    newTabContent.style.display = "none";
    newTabContent.innerHTML = `
        <h4>${day}日目のスケジュール一覧</h4>
        <ul id="scheduleList${day}"></ul>
        <a href="/schedule/create/${day}" class="tablinks">新しいスケジュールを追加</a>`;

    // タブボタンを追加
    const tabContainer = document.getElementById("tabContainer");
    const addTabButton = document.getElementById("addTabButton");
    tabContainer.insertBefore(newTabButton, addTabButton);

    // 新しいタブコンテンツを本文に追加
    document.body.appendChild(newTabContent);
}

// タブ削除用の関数
function removeTab(day) {
    // タブボタンとタブコンテンツを削除
    const tabButton = document.querySelector(`.tablinks[onclick="openTab(event, 'tab${day}')"]`);
    const tabContent = document.getElementById(`tab${day}`);
    if (tabButton) tabButton.remove();
    if (tabContent) tabContent.remove();

    // 最後に残ったタブをデフォルトで開く
    const lastTabButton = document.querySelector(".tablinks");
    if (lastTabButton) lastTabButton.click();
}

// 新しいタブを追加する関数 (必要な場合のみ)
function addTab() {
    if (tabCount >= maxTabs) {
        alert("これ以上タブを追加できません。");
        return;
    }

    tabCount++;
    createTab(tabCount);
}
