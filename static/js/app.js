// Dental Lab Manager - Interactive scripts (Arabic & RTL)

document.addEventListener("DOMContentLoaded", () => {
    // 1. البحث الفوري السريع عن المرضى
    const searchInput = document.getElementById("global-search-input");
    const searchResults = document.getElementById("global-search-results");

    if (searchInput && searchResults) {
        let debounceTimer;
        searchInput.addEventListener("input", (e) => {
            clearTimeout(debounceTimer);
            const query = e.target.value.trim();

            if (query.length < 2) {
                searchResults.classList.add("hidden");
                searchResults.innerHTML = "";
                return;
            }

            debounceTimer = setTimeout(() => {
                fetch(`/api/search?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.length === 0) {
                            searchResults.innerHTML = `<div class="p-3 text-xs text-slate-500 text-center font-medium">لم يتم العثور على أي مريض بالاسم "${query}"</div>`;
                        } else {
                            searchResults.innerHTML = data.map(item => `
                                <a href="${item.url}" class="flex items-center justify-between p-3 hover:bg-sky-50 transition border-b border-slate-100 last:border-b-0 text-right">
                                    <div>
                                        <div class="font-bold text-slate-800 text-xs">${item.name}</div>
                                        <div class="text-[11px] text-slate-400 font-mono mt-0.5">${item.phone}</div>
                                    </div>
                                    <div class="text-xs font-bold ${item.remaining_balance > 0 ? 'text-amber-600' : 'text-emerald-600'}">
                                        ${item.remaining_balance > 0 ? `المتبقي: ${item.remaining_balance} درهم` : 'تم السداد'}
                                    </div>
                                </a>
                            `).join("");
                        }
                        searchResults.classList.remove("hidden");
                    })
                    .catch(err => console.error("Search error:", err));
            }, 250);
        });

        // إخفاء النتائج عند النقر بالخارج
        document.addEventListener("click", (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.add("hidden");
            }
        });
    }

    // 2. إدارة النوافذ المنبثقة (Modals)
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove("hidden");
            modal.classList.add("flex");
        }
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add("hidden");
            modal.classList.remove("flex");
        }
    };

    // 3. نسخ الرابط للحافظة
    window.copyToClipboard = function(text, successMessage = "تم نسخ الرابط بنجاح !") {
        navigator.clipboard.writeText(text).then(() => {
            alert(successMessage);
        }).catch(err => {
            console.error("Erreur copie", err);
        });
    };
});
