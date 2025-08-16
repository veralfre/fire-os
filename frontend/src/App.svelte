<script>
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';
  let tableEl;
  let transactions = [];
  let search = '';
  let loading = true;
  let error = '';
  let netWorthHistory = [];
  let labels = [];

  // Fetch all paginated transactions by month/year
  async function fetchAllTransactions() {
  let page = 1;
    let allTx = [];
    let hasMore = true;
    while (hasMore) {
      const res = await fetch(`http://localhost:8000/accounts/api/transactions?page=${page}`);
      if (!res.ok) throw new Error('Failed to fetch transactions');
      const result = await res.json();
      // Use 'transactions' property from API response
      if (Array.isArray(result.transactions)) {
        if (result.transactions.length === 0) break;
        allTx = allTx.concat(result.transactions);
        // If API returns less than 100, it's the last page
        hasMore = result.transactions.length === 100;
        page++;
      } else {
        hasMore = false;
      }
    }
    return allTx;
  }

  function calculateNetWorth(txList) {
    // Group by year-month, sum avg_amount * count_amount for each period
    const map = {};
    txList.forEach(tx => {
      const key = `${tx.year}-${String(tx.month).padStart(2, '0')}`;
      if (!map[key]) map[key] = 0;
      map[key] += parseFloat(tx.avg_amount) * parseInt(tx.count_amount);
    });
    // Sort by period
    const sorted = Object.entries(map).sort(([a], [b]) => a.localeCompare(b));
    labels = sorted.map(([period]) => period);
    netWorthHistory = sorted.map(([_, value]) => value);
  }

  let chartInstance;
  let chartCanvas;

  import { tick } from 'svelte';

  // Load DataTables JS and CSS from CDN
  function loadDataTables() {
    if (!document.getElementById('dt-css')) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = 'https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css';
      link.id = 'dt-css';
      document.head.appendChild(link);
    }
    if (!window.jQuery) {
      const scriptJQ = document.createElement('script');
      scriptJQ.src = 'https://code.jquery.com/jquery-3.7.0.min.js';
      scriptJQ.onload = () => loadDT();
      document.body.appendChild(scriptJQ);
    } else {
      loadDT();
    }
    function loadDT() {
      if (!window.jQuery.fn.DataTable) {
        const scriptDT = document.createElement('script');
        scriptDT.src = 'https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js';
        scriptDT.onload = () => {
          if (tableEl && window.jQuery) {
            window.jQuery(tableEl).DataTable();
          }
        };
        document.body.appendChild(scriptDT);
      } else {
        if (tableEl && window.jQuery) {
          window.jQuery(tableEl).DataTable();
        }
      }
    }
  }

  onMount(async () => {
    try {
      const txList = await fetchAllTransactions();
      transactions = txList;
      calculateNetWorth(txList);
      // Wait for canvas to be available
      await tick();
      drawChart();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  });

  function drawChart() {
    if (!chartCanvas) return;
    const ctx = chartCanvas.getContext('2d');
    if (chartInstance) chartInstance.destroy();
    chartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Net Worth',
          data: netWorthHistory,
          backgroundColor: 'rgba(75,192,192,0.2)',
          borderColor: 'rgba(75,192,192,1)',
          borderWidth: 2,
          fill: true,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
          title: { display: true, text: 'Net Worth Over Time' }
        },
        scales: {
          x: { title: { display: true, text: 'Period' } },
          y: { title: { display: true, text: 'Net Worth' } }
        }
      }
    });
  }

  $: filtered = transactions.filter(tx =>
    Object.values(tx).some(val =>
      String(val).toLowerCase().includes(search.toLowerCase())
    )
  );
</script>

<main>
  <h1>Net Worth Dashboard</h1>
  {#if loading}
    <p>Loading...</p>
  {:else if error}
    <p style="color: red">{error}</p>
  {:else}
    <section>
      <h2>Net Worth Progression</h2>
  <canvas id="netWorthChart" width="800" height="300" bind:this={chartCanvas}></canvas>
    </section>
    <section>
      <h2>Transactions</h2>
      <input
        type="text"
        placeholder="Search transactions..."
        bind:value={search}
        style="margin-bottom:1rem;padding:0.5rem;width:100%;max-width:400px;"
      />
      {#if Array.isArray(filtered) && filtered.length > 0}
        <table bind:this={tableEl} id="transactionsTable" class="display" style="width:100%">
          <thead>
            <tr>
              <th>Date</th>
              <th>Amount</th>
              <th>Category ID</th>
              <th>Description</th>
              <th>Type</th>
            </tr>
          </thead>
          <tbody>
            {#each filtered as tx}
              <tr>
                <td>{tx.date}</td>
                <td>{tx.amount}</td>
                <td>{tx.category_id}</td>
                <td>{tx.description}</td>
                <td>{tx.transaction_type}</td>
              </tr>
            {/each}
          </tbody>
        </table>
        <pre>First transaction debug: {JSON.stringify(filtered[0], null, 2)}</pre>
        {@html `<script>setTimeout(function(){(${loadDataTables.toString()})();}, 0);</script>`}
      {:else}
        <p>No transactions found.</p>
        <pre>Debug: {JSON.stringify(transactions, null, 2)}</pre>
      {/if}
    </section>
  {/if}
</main>

<style>
  main {
    padding: 2rem;
    font-family: sans-serif;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    margin-top: 1rem;
  }
  th, td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
  }
  th {
    background: #f4f4f4;
  }
  input {
    font-size: 1rem;
  }
  section {
    margin-bottom: 2rem;
  }
</style>
