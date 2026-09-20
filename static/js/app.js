// Dental Lab Manager - Interactive scripts

document.addEventListener("DOMContentLoaded", () => {
    // 1. Recherche instantanée rapide
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
                            searchResults.innerHTML = `<div class="p-3 text-sm text-slate-500 text-center">Aucun patient trouvé pour "${query}"</div>`;
                        } else {
                            searchResults.innerHTML = data.map(item => `
                                <a href="${item.url}" class="flex items-center justify-between p-3 hover:bg-sky-50 transition border-b border-slate-100 last:border-b-0">
                                    <div>
                                        <div class="font-medium text-slate-800">${item.name}</div>
                                        <div class="text-xs text-slate-500">${item.phone}</div>
                                    </div>
                                    <div class="text-xs font-semibold ${item.remaining_balance > 0 ? 'text-amber-600' : 'text-emerald-600'}">
                                        ${item.remaining_balance > 0 ? `Solde: ${item.remaining_balance} DH` : 'Soldé'}
                                    </div>
                                </a>
                            `).join("");
                        }
                        searchResults.classList.remove("hidden");
                    })
                    .catch(err => console.error("Search error:", err));
            }, 250);
        });

        // Masquer les résultats si clic extérieur
        document.addEventListener("click", (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.add("hidden");
            }
        });
    }

    // 2. Gestion des Modales génériques
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

    // 3. Copie dans le presse-papier
    window.copyToClipboard = function(text, successMessage = "Lien copié !") {
        navigator.clipboard.writeText(text).then(() => {
            alert(successMessage);
        }).catch(err => {
            console.error("Erreur copie", err);
        });
    };
});
