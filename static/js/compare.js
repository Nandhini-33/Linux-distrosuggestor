/**
 * Comparison Tool Dynamic Switcher
 */

document.addEventListener("DOMContentLoaded", () => {
  const select1 = document.getElementById("selectDistro1");
  const select2 = document.getElementById("selectDistro2");
  const select3 = document.getElementById("selectDistro3");

  function refreshComparison() {
    const d1 = select1 ? select1.value : "linux-mint";
    const d2 = select2 ? select2.value : "ubuntu";
    const d3 = select3 ? select3.value : "";

    let url = `/compare?d1=${encodeURIComponent(d1)}&d2=${encodeURIComponent(d2)}`;
    if (d3) {
      url += `&d3=${encodeURIComponent(d3)}`;
    }
    window.location.href = url;
  }

  if (select1) select1.addEventListener("change", refreshComparison);
  if (select2) select2.addEventListener("change", refreshComparison);
  if (select3) select3.addEventListener("change", refreshComparison);
});
