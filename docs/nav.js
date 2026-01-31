(function () {
    var path = window.location.pathname || "/";
    var file = path.split("/").filter(Boolean).pop() || "index.html";
    var pageKey = file.replace(".html", "");
    var reportKey = "";

    if (file === "report.html") {
        var params = new URLSearchParams(window.location.search);
        var reportFile = params.get("file") || "";
        if (reportFile.indexOf("reports/after.md") === 0) {
            reportKey = "report-after";
        } else if (reportFile.indexOf("reports/diff.md") === 0) {
            reportKey = "report-diff";
        } else if (reportFile.indexOf("reports/before.md") === 0) {
            reportKey = "report-before";
        } else {
            reportKey = "report-before";
        }
    }

    var activeKey = reportKey || pageKey;
    var links = document.querySelectorAll("[data-nav]");
    links.forEach(function (link) {
        if (link.getAttribute("data-nav") === activeKey) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });
})();
