(() => {
"use strict";
const input = document.querySelector("#report-search");
if (input) {
  const cards = Array.from(document.querySelectorAll("[data-filter-container] [data-search]"));
  const counter = document.querySelector(".filter-count");
  function apply() {
    const query = input.value.trim().toLocaleLowerCase();
    let count = 0;
    for (const card of cards) {
      const show = card.dataset.search.toLocaleLowerCase().includes(query);
      card.hidden = !show;
      if (show) count++;
    }
    if (counter) counter.textContent = "显示 " + count + " / " + cards.length + " 篇";
  }
  input.addEventListener("input", apply); apply();
}
const metric = document.querySelector("#metric-search");
if (metric) metric.addEventListener("input", () => {
  const query = metric.value.trim().toLocaleLowerCase();
  for (const row of document.querySelectorAll("[data-metric-row]")) {
    row.hidden = !row.dataset.metricRow.toLocaleLowerCase().includes(query);
  }
});
const download = document.querySelector("[data-download-table]");
if (download) download.addEventListener("click", () => {
  const lines = [];
  for (const table of document.querySelectorAll(".table-wrap table")) {
    lines.push([table.caption.textContent.trim()]);
    for (const row of table.querySelectorAll("tr")) lines.push(Array.from(row.cells).map(c => c.textContent.trim()));
    lines.push([]);
  }
  const csv = lines.map(row => row.map(c => '"' + c.replaceAll('"','""') + '"').join(",")).join("\r\n");
  const url = URL.createObjectURL(new Blob(["\ufeff",csv], {type:"text/csv;charset=utf-8"}));
  const a=document.createElement("a");a.href=url;a.download="financial-metrics.csv";
  document.body.appendChild(a);a.click();a.remove();
  setTimeout(() => URL.revokeObjectURL(url),1000);
});
})();