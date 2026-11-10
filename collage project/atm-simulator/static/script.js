// ================= LOGIN PAGE =================
const loginBtn = document.getElementById('loginBtn');

if (loginBtn) {
    loginBtn.addEventListener('click', async () => {
        const accountNo = document.getElementById('accountNo').value.trim();
        const pin = document.getElementById('pin').value.trim();
        const errorMsg = document.getElementById('errorMsg');

        if (!accountNo || !pin) {
            errorMsg.textContent = "Please fill all fields!";
            return;
        }

        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ account_no: accountNo, pin: pin })
        });
        const data = await res.json();

        if (data.success) {
            window.location.href = '/dashboard';
        } else {
            errorMsg.textContent = data.message;
            document.getElementById('pin').value = '';
        }
    });

    // Enter key support
    document.getElementById('pin').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loginBtn.click();
    });
}

// ================= DASHBOARD =================
if (document.getElementById('balanceDisplay')) {
    let currentBalance = 0;

    // Load balance
    async function loadBalance() {
        const res = await fetch('/api/balance');
        const data = await res.json();
        if (data.success) {
            currentBalance = data.balance;
            document.getElementById('userName').textContent = data.name;
            document.getElementById('accDisplay').textContent = data.account_no;
            updateBalanceDisplay();
        } else {
            window.location.href = '/';
        }
    }

    function updateBalanceDisplay() {
        document.getElementById('balanceDisplay').textContent =
            '₹' + currentBalance.toLocaleString('en-IN', { minimumFractionDigits: 2 });
    }

    // Toast notification
    function showToast(message, isError = false) {
        const toast = document.getElementById('msg');
        toast.textContent = message;
        toast.classList.remove('error');
        if (isError) toast.classList.add('error');
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }

    // Modal helpers
    const modal = document.getElementById('modal');
    const modalBox = document.getElementById('modalBox');

    function closeModal() {
        modal.classList.remove('active');
    }

    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // ---------- Withdraw / Deposit ----------
    function openAmountModal(title, endpoint) {
        modalBox.innerHTML = `
            <h3>${title}</h3>
            <input type="number" id="amountInput" placeholder="Enter amount (₹)" min="1">
            <div class="btn-row">
                <button class="btn-confirm" id="confirmBtn">Confirm</button>
                <button class="btn-cancel" id="cancelBtn">Cancel</button>
            </div>
        `;
        modal.classList.add('active');
        document.getElementById('amountInput').focus();

        document.getElementById('cancelBtn').onclick = closeModal;

        document.getElementById('confirmBtn').onclick = async () => {
            const amount = parseFloat(document.getElementById('amountInput').value);
            if (!amount || amount <= 0) {
                showToast('Enter a valid amount!', true);
                return;
            }
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount: amount })
            });
            const data = await res.json();
            if (data.success) {
                currentBalance = data.balance;
                updateBalanceDisplay();
                closeModal();
                showToast(data.message);
            } else {
                showToast(data.message, true);
            }
        };
    }

    document.getElementById('btnWithdraw').onclick = () =>
        openAmountModal('💸 Withdraw Amount', '/api/withdraw');
    document.getElementById('btnDeposit').onclick = () =>
        openAmountModal('💰 Deposit Amount', '/api/deposit');

    // ---------- Mini Statement ----------
    document.getElementById('btnStatement').onclick = async () => {
        const res = await fetch('/api/statement');
        const data = await res.json();

        let rows = '';
        if (data.transactions.length === 0) {
            rows = '<tr><td colspan="3" style="text-align:center;color:#7f8c8d;">No transactions yet</td></tr>';
        } else {
            data.transactions.forEach(t => {
                const color = t.type === 'DEPOSIT' ? '#27ae60' : '#e74c3c';
                rows += `
                    <tr>
                        <td>${t.timestamp.split('.')[0]}</td>
                        <td style="color:${color};font-weight:600;">${t.type}</td>
                        <td style="color:${color};">₹${t.amount.toFixed(2)}</td>
                    </tr>
                `;
            });
        }

        modalBox.innerHTML = `
            <h3>📄 Mini Statement</h3>
            <table class="statement-table">
                <thead>
                    <tr><th>Date/Time</th><th>Type</th><th>Amount</th></tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
            <div class="btn-row" style="margin-top:15px;">
                <button class="btn-cancel" onclick="document.getElementById('modal').classList.remove('active')">Close</button>
            </div>
        `;
        modal.classList.add('active');
    };

    // ---------- Refresh Balance ----------
    document.getElementById('btnBalance').onclick = () => {
        loadBalance();
        showToast('Balance refreshed!');
    };

    // ---------- Logout ----------
    document.getElementById('logoutBtn').onclick = async () => {
        await fetch('/api/logout');
        window.location.href = '/';
    };

    // Init
    loadBalance();
}