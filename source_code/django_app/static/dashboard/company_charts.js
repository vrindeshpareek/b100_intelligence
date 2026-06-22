const colors={blue:"#2E75B6",navy:"#1F4E79",green:"#2ECC71",orange:"#F39C12",red:"#E74C3C",light:"#DCE6F1"};
const base={responsive:true,maintainAspectRatio:false,interaction:{mode:"index",intersect:false},plugins:{legend:{position:"bottom"}}};
const clean=v=>v==null?null:Number(v);
fetch(`/api/v1/companies/${window.B100_SYMBOL}/charts/`)
  .then(r=>{if(!r.ok)throw new Error("Chart data unavailable");return r.json()})
  .then(d=>{
    document.getElementById("chart-status").remove();
    new Chart("revenueProfit",{type:"bar",data:{labels:d.years,datasets:[
      {label:"Sales",data:d.revenue_profit.sales,backgroundColor:colors.blue},
      {label:"Net Profit",data:d.revenue_profit.net_profit,backgroundColor:colors.green},
      {label:"OPM %",data:d.revenue_profit.opm_pct,type:"line",borderColor:colors.orange,yAxisID:"y1"}
    ]},options:{...base,scales:{y1:{position:"right",grid:{drawOnChartArea:false}}}}});
    new Chart("balanceSheet",{type:"bar",data:{labels:d.years,datasets:[
      {label:"Equity + Reserves",data:d.balance_sheet.equity_reserves,backgroundColor:colors.green},
      {label:"Borrowings",data:d.balance_sheet.borrowings,backgroundColor:colors.red},
      {label:"Other Liabilities",data:d.balance_sheet.other_liabilities,backgroundColor:colors.orange}
    ]},options:{...base,scales:{x:{stacked:true},y:{stacked:true}}}});
    new Chart("cashFlow",{type:"bar",data:{labels:d.years,datasets:[
      {label:"Operating",data:d.cash_flow.operating,backgroundColor:colors.green},
      {label:"Investing",data:d.cash_flow.investing,backgroundColor:colors.blue},
      {label:"Financing",data:d.cash_flow.financing,backgroundColor:colors.orange}
    ]},options:base});
    new Chart("epsDividend",{type:"line",data:{labels:d.years,datasets:[
      {label:"EPS",data:d.eps_dividend.eps,borderColor:colors.navy},
      {label:"Dividend Payout %",data:d.eps_dividend.dividend_payout_pct,borderColor:colors.green,yAxisID:"y1"}
    ]},options:{...base,scales:{y1:{position:"right",grid:{drawOnChartArea:false}}}}});
    new Chart("debtEquity",{type:"line",data:{labels:d.years,datasets:[
      {label:"Borrowings",data:d.balance_sheet.borrowings,borderColor:colors.red,backgroundColor:"#e74c3c33",fill:true},
      {label:"Reserves",data:d.balance_sheet.reserves,borderColor:colors.green,backgroundColor:"#2ecc7133",fill:true}
    ]},options:base});
    new Chart("cagrRadar",{type:"radar",data:{labels:["Sales","Profit","Stock CAGR","ROE"],datasets:d.cagr_radar.periods.map((p,i)=>({
      label:p,data:[d.cagr_radar.sales[i],d.cagr_radar.profit[i],d.cagr_radar.stock[i],d.cagr_radar.roe[i]],
      borderColor:[colors.navy,colors.green,colors.orange,colors.red][i%4],backgroundColor:"transparent"
    }))},options:base});
    new Chart("margins",{type:"line",data:{labels:d.years,datasets:[
      {label:"OPM %",data:d.margins.opm_pct,borderColor:colors.blue},
      {label:"Net Profit Margin %",data:d.margins.net_profit_margin_pct,borderColor:colors.green}
    ]},options:base});
    const score=clean(d.health.overall)||0;
    new Chart("healthGauge",{type:"doughnut",data:{labels:["Score","Remaining"],datasets:[{data:[score,100-score],backgroundColor:[score>=80?colors.green:score>=60?colors.blue:score>=40?colors.orange:colors.red,colors.light],borderWidth:0}]},options:{...base,circumference:180,rotation:270,cutout:"72%"}});
  })
  .catch(e=>document.getElementById("chart-status").textContent=e.message);
