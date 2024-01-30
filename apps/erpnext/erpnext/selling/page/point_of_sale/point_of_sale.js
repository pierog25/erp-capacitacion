frappe.provide('erpnext.PointOfSale');
{% include 'erpnext/selling/page/point_of_sale/payment_niubiz.js' %};
frappe.pages['point-of-sale'].on_page_load = async function(wrapper) {

	const get_closing = await frappe.db.get_list("CIERRE TIENDA",{
		"filters":[["fecha_cierre","=",moment(new Date()).format("YYYY-MM-DD")],["docstatus","=",1]],
		"limit":"None"
	})

	if(get_closing.length > 0 && !["77050071@shalomcontrol.com","tienda@shalom.com.pe","Administrator","48191841@shalomcontrol.com"].includes(frappe.user.name)){
		frappe.throw("No puede generar ventas despues de su cierre de shalom store")
		frappe.utils.play_sound("error");
		return false;
	}

	frappe.ui.make_app_page({
		parent: wrapper,
		title: __('Point of Sale'),
		single_column: true
	});

	frappe.require('assets/js/point-of-sale.min.js', function() {
		wrapper.pos = new erpnext.PointOfSale.Controller(wrapper);
		window.cur_pos = wrapper.pos;
	});
};

frappe.pages['point-of-sale'].refresh = async function(wrapper) {

	if (document.scannerDetectionData) {
		onScan.detachFrom(document);
		wrapper.pos.wrapper.html("");
		wrapper.pos.check_opening_entry();
	}
};