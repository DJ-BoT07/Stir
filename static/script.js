document.addEventListener('DOMContentLoaded', () => {
    const runButton = document.getElementById('run-script-button');
    const resultDiv = document.getElementById('result');

    runButton.addEventListener('click', () => {
        resultDiv.innerHTML = "Running script, please wait...";
        fetch('/run-script', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                const trend = data.data;
                const date = new Date(trend.date_time).toLocaleString();
                resultDiv.innerHTML = `
                    <p class="mb-4">These are the most happening topics as on ${date}</p>
                    <ul class="list-disc pl-5 mb-4">
                        <li>${trend.nameoftrend1}</li>
                        <li>${trend.nameoftrend2}</li>
                        <li>${trend.nameoftrend3}</li>
                        <li>${trend.nameoftrend4}</li>
                        <li>${trend.nameoftrend5}</li>
                    </ul>
                    <p class="mb-4">The IP address used for this query was ${trend.ip_address}.</p>
                    <button id="run-script-button" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                        Click here to run the query again
                    </button>
                `;
            } else {
                resultDiv.innerHTML = `<p class="text-red-500">Error: ${data.error}</p>`;
            }
        })
        .catch(error => {
            resultDiv.innerHTML = `<p class="text-red-500">An error occurred: ${error}</p>`;
        });
    });
});
