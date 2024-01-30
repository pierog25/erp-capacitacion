
frappe.provide('frappe.tablero_finanzas');
frappe.pages['tablero-finanzas'].on_page_load = function(wrapper) {
	let me = this;
	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Tablero Finanzas',
		single_column: true
	});
	page.main.html(frappe.render_template('tablero_finanzas', {}));


	// const data = {
	// 	labels: ["12am-3am", "3am-6pm", "6am-9am", "9am-12am",
	// 		"12pm-3pm", "3pm-6pm", "6pm-9pm", "9am-12am"
	// 	],
	// 	datasets: [
	// 		{
	// 			name: "Some Data", type: "bar",
	// 			values: [25, 40, 30, 35, 8, 52, 17, -4]
	// 		},
	// 		{
	// 			name: "Another Set", type: "line",
	// 			values: [25, 50, -10, 15, 18, 32, 27, 14]
	// 		}
	// 	]
	// }
	//
	// const chart = new frappe.Chart("#chart", {  // or a DOM element,
	// 	// new Chart() in case of ES6 module with above usage
	// 	title: "My Awesome Chart",
	// 	data: data,
	// 	type: 'axis-mixed', // or 'bar', 'line', 'scatter', 'pie', 'percentage'
	// 	height: 250,
	// 	colors: ['#7cd6fd', '#743ee2']
	// })


	const data = {
		labels: ['Bootstrap', 'Popper', 'Other'],
		datasets: [
			{
				backgroundColor: ['#007bff','#28a745','#333333'],
				borderWidth: 0,
				data: [74, 11, 40]
			}
		]
	}

	const chart = new frappe.Chart("#chart", {  // or a DOM element,
		// new Chart() in case of ES6 module with above usage
		title: "My Awesome Chart",
		data: data,
		type: 'donut', // or 'bar', 'line', 'scatter', 'pie', 'percentage'
		height: 250,
		colors: ['#007bff','#28a745','#333333','#c3e6cb','#dc3545','#6c757d']
	})



}