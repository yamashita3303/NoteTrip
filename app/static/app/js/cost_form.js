document.addEventListener('DOMContentLoaded', function() {
    const walletRadios = document.querySelectorAll('input[name="cost_wallet"]');
    const payerGroup = document.getElementById('payer-group');
    const moneyGroup = document.getElementById('money-group');
    const addpayersGroup = document.getElementById('addpayers-group');
    const subpayersGroup = document.getElementById('subpayers-group');
    const payerInput = document.getElementById('id_payment_payers');  // 支払者の入力フィールド
    const moneyInput = document.getElementById('id_payment_money');  // 費用の入力フィールド

    walletRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'personal') {  // 'personal'を選択した場合
                payerGroup.style.display = 'block';  // 支払者を表示
                payerInput.setAttribute('required', 'required');  // 必須にする
                moneyGroup.style.display = 'block';  // 費用を表示
                moneyInput.setAttribute('required', 'required');  // 必須にする
                addpayersGroup.style.display = 'block';  // 支払者、費用追加ボタンを表示
                subpayersGroup.style.display = 'block';  // 支払者、費用削除ボタンを表示
            } else {
                payerGroup.style.display = 'none';  // 支払者を非表示
                payerInput.removeAttribute('required');  // 必須を外す
                moneyGroup.style.display = 'block';  // 費用を表示
                moneyInput.setAttribute('required', 'required');  // 必須にする
                addpayersGroup.style.display = 'none';  // 支払者、費用追加ボタンを表示
                subpayersGroup.style.display = 'none';  // 支払者、費用削除ボタンを表示
            }
        });
    });

    // ページロード時に初期状態を設定
    if (document.querySelector('input[name="cost_wallet"]:checked')) {
        document.querySelector('input[name="cost_wallet"]:checked').dispatchEvent(new Event('change'));
    }
});

// 新しい支払者、費用を追加する関数
function addPayers() {
    // 支払者、費用フォームコンテナを取得
    const payersFormContainer = document.getElementById("payers-form-container");

    // 新しい支払者、費用用のdivを作成、適用
    const newPayersDiv = document.createElement("div");
    newPayersDiv.classList.add("form-group");

    // 支払者名のラベル作成
    const payersLabel = document.createElement("label");
    payersLabel.innerText = "支払者";

    // 支払者名フィールドを作成
    const payersInput = document.createElement("input");
    payersInput.type = "text";
    payersInput.name = "payment_payers";
    payersInput.classList.add("form-control");

    // 費用のラベル作成
    const moneyLabel = document.createElement("label");
    moneyLabel.innerText = "費用";

    // 費用フィールドを作成
    const moneyInput = document.createElement("input");
    moneyInput.type = "text";
    moneyInput.name = "payment_money";
    moneyInput.classList.add("form-control");

    // 支払者と費用を新しい材料divに追加
    newPayersDiv.appendChild(payersLabel);
    newPayersDiv.appendChild(payersInput);
    newPayersDiv.appendChild(moneyLabel);
    newPayersDiv.appendChild(moneyInput);

    // 支払者、費用フォームコンテナに新しい材料divを追加
    payersFormContainer.appendChild(newPayersDiv);
}

// 支払者、費用を削除する関数
function subPayers() {
    const payersFormContainer = document.getElementById("payers-form-container");

    // 最低一つは残るように調整
    if (payersFormContainer.children.length > 2) {
        payersFormContainer.removeChild(payersFormContainer.lastElementChild);
    }
}
