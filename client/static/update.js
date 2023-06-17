// ====================================================================================================
// Update values every 15 seconds

function updatePrices() {
	// get the new prices
	fetch("/api/stock_data")
		.then((response) => response.json())
		.then((data) => {
			// update the time of the last update
			data.meta.current_prices_date_logged =
				data.meta.current_prices_date_logged.split(".")[0];
			data.meta.closings_date_logged =
				data.meta.closings_date_logged.split(".")[0];
			document.getElementById("current_prices_update_time").textContent =
				data.meta.current_prices_date_logged;
			document.getElementById(
				"previous_closing_prices_update_time"
			).textContent = data.meta.closings_date_logged;

			// update the prices and changes in the stocks tab
			for (let ticker in data["data"]) {
				let currentPrice = data["data"][ticker]["current_price"];
				let previousClosingPrice =
					data["data"][ticker]["previous_closing_price"];
				let change = currentPrice - previousClosingPrice;
				let changePercentage = (change / previousClosingPrice) * 100;
				currentPrice = currentPrice.toFixed(2);
				previousClosingPrice = previousClosingPrice.toFixed(2);
				change = change.toFixed(2);
				changePercentage = changePercentage.toFixed(2);

				document.getElementById(
					"stocks-tab-price-" + ticker
				).textContent = currentPrice;

				if (changePercentage > 0) {
					document.getElementById(
						"stocks-tab-change-" + ticker
					).textContent = "+" + changePercentage + "%";
					// change text-danger to text-success if the div contains text-danger
					if (
						document
							.getElementById("stocks-tab-change-" + ticker)
							.classList.contains("text-danger")
					) {
						document
							.getElementById("stocks-tab-change-" + ticker)
							.classList.remove("text-danger");
						document
							.getElementById("stocks-tab-change-" + ticker)
							.classList.add("text-success");
					}
					// update the prices and changes in the main panes
					document.getElementById("diff-" + ticker).textContent =
						"+" + change + " (+" + changePercentage + "%)";
					// change text-danger to text-success if the div contains text-danger
					if (
						document
							.getElementById("diff-" + ticker)
							.classList.contains("text-danger")
					) {
						document
							.getElementById("diff-" + ticker)
							.classList.remove("text-danger");
						document
							.getElementById("diff-" + ticker)
							.classList.add("text-success");
					}
				} else {
					document.getElementById(
						"stocks-tab-change-" + ticker
					).textContent = changePercentage + "%";
					// change text-success to text-danger if the div contains text-success
					if (
						document
							.getElementById("stocks-tab-change-" + ticker)
							.classList.contains("text-success")
					) {
						document
							.getElementById("stocks-tab-change-" + ticker)
							.classList.remove("text-success");
						document
							.getElementById("stocks-tab-change-" + ticker)
							.classList.add("text-danger");
					}
					// update the prices and changes in the main panes
					document.getElementById("diff-" + ticker).textContent =
						change + " (" + changePercentage + "%)";
					// change text-success to text-danger if the div contains text-success
					if (
						document
							.getElementById("diff-" + ticker)
							.classList.contains("text-success")
					) {
						document
							.getElementById("diff-" + ticker)
							.classList.remove("text-success");
						document
							.getElementById("diff-" + ticker)
							.classList.add("text-danger");
					}
				}

				// update the prices and changes in the main panes
				document.getElementById("price-" + ticker).textContent =
					currentPrice;
				document.getElementById("prev-close-" + ticker).textContent =
					previousClosingPrice;
			}
		})
		.catch((error) => {
			console.error("Error:", error);
		});
}

setInterval(updatePrices, 2500);
