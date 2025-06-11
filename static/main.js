// JS file for the QOTD app

var PAGE = "main";

function open(page) {
    console.log("Opening page: " + page + " from " + PAGE);m, m, 
    if (page == PAGE) return;
    var currentPage = document.getElementById(PAGE);
    var newPage = document.getElementById(page);
    currentPage.setAttribute("hidden", "true");
    newPage.removeAttribute("hidden");
    PAGE = page;
    document.getElementsByTagName("title")[0].innerHTML = "QOTD - " + newPage.children.getElementById("title").innerHTML;
}