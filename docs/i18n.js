(function () {
    var stored = localStorage.getItem("lang");
    var browser = (navigator.language || "en").toLowerCase();
    var lang = stored || (browser.indexOf("es") === 0 ? "es" : "en");
    var dict = null;

    function t(key) {
        if (!dict || !dict[lang]) return key;
        return dict[lang][key] || key;
    }

    function apply() {
        if (!dict) return;
        document.documentElement.setAttribute("lang", lang);
        document.querySelectorAll("[data-i18n]").forEach(function (el) {
            var key = el.getAttribute("data-i18n");
            el.textContent = t(key);
        });
        document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
            var key = el.getAttribute("data-i18n-placeholder");
            el.setAttribute("placeholder", t(key));
        });
        var toggle = document.getElementById("lang-toggle");
        if (toggle) {
            toggle.textContent = lang.toUpperCase();
            toggle.addEventListener("click", function () {
                var next = lang === "es" ? "en" : "es";
                localStorage.setItem("lang", next);
                window.location.reload();
            });
        }
        window.i18n = { lang: lang, t: t };
    }

    fetch("i18n.json", { cache: "no-store" })
        .then(function (res) { return res.ok ? res.json() : null; })
        .then(function (data) {
            if (!data) return;
            dict = data;
            apply();
        })
        .catch(function () {
            window.i18n = { lang: lang, t: t };
        });
})();
