odoo.define('geneye_dashboard.dashboard', function (require) {
  "use strict";
  var ajax = require('web.ajax');

  async function refreshData() {
    const d = await ajax.jsonRpc('/geneye/data', 'call', {});
    document.getElementById("status").textContent = d.Status ?? "—";
    document.getElementById("timestamp").textContent = d.Timestamp ?? "—";
    document.getElementById("hours").textContent = d.Running_Hours != null ? (d.Running_Hours + " h") : "—";
    document.getElementById("kwh").textContent   = d.Power_kVA != null ? (d.Power_kVA + " kVA") : "—";
    document.getElementById("fuel").textContent  = d.Fuel_Level != null ? (d.Fuel_Level + " %") : "—";
    document.getElementById("rpm").textContent   = d.Engine_RPM != null ? (d.Engine_RPM + " rpm") : "—";
    document.getElementById("temp").textContent  = d.Coolant_Temp != null ? (d.Coolant_Temp + " °C") : "—";
    document.getElementById("voltage").textContent = d.Battery_Voltage != null ? (d.Battery_Voltage + " V") : "—";
    document.getElementById("freq").textContent  = d.Frequency != null ? (d.Frequency + " Hz") : "—";
    document.getElementById("power").textContent = d.Power_kVA != null ? (d.Power_kVA + " kVA") : "—";
  }

  async function fetchHistory() {
    const d = await ajax.jsonRpc('/geneye/history', 'call', {});
    const ts = d.Timestamp || [];
    const rh = d.Running_Hours || [];
    const fl = d.Fuel_Level || [];
    const pk = d.Power_kVA || [];
    if (window.Chart) {
      const opts = { responsive:true, plugins:{ legend:{ display:false } } };
      new Chart(document.getElementById('runHoursChart'), { type:'line', data:{ labels:ts, datasets:[{ data:rh, borderColor:'#0f4c9a' }] }, options:opts });
      new Chart(document.getElementById('fuelChart'), { type:'line', data:{ labels:ts, datasets:[{ data:fl, borderColor:'#28a745' }] }, options:opts });
      new Chart(document.getElementById('powerChart'), { type:'line', data:{ labels:ts, datasets:[{ data:pk, borderColor:'#ff9800' }] }, options:opts });
    }
  }

  setInterval(refreshData, 5000);
  refreshData();
  fetchHistory();
});
