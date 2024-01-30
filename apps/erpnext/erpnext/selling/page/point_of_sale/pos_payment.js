/* eslint-disable no-unused-vars */
erpnext.PointOfSale.Payment = class {
	constructor({ events, wrapper }) {
		this.wrapper = wrapper;
		this.events = events;
		this.init_component();
	}

	init_component() {
		this.prepare_dom();
		this.initialize_numpad();
		this.bind_events();
		this.attach_shortcuts();
	}

	prepare_dom() {
		var style_2 = ["Administrator", "70279517@shalomcontrol.com"].includes(frappe.user.name) ? "block":"none";
		var style = ["77050071@shalomcontrol.com","tienda@shalom.com.pe","Administrator","48191841@shalomcontrol.com","77050071@shalomcontrol.com", "70279517@shalomcontrol.com"].includes(frappe.user.name) ? "block":"none";
		var html_options = `
			<div class="row text-center">
				<div class="form-check form-switch col-md-4 style="display: ${style}">
					<input class="form-check-input check-options" type="checkbox" id="checkPinpad" name="checkPinpad" value="Pago por PINPAD">
					<label class="form-check-label" for="checkPinpad"><strong>PINPAD</strong></label>
				</div>
				<div class="form-check form-switch col-md-4 style="display: ${style}">
					<input class="form-check-input check-options" type="checkbox" id="checkQR" name="checkQR" value="QR">
					<label class="form-check-label" for="checkQR"><strong>QR</strong></label>
				</div>
				<div class="form-check form-switch col-md-4" style="display: ${style}">
					<input class="form-check-input check-options" type="checkbox" id="checkPlanilla" name="checkPlanilla" value="Planilla">
					<label class="form-check-label" for="checkPlanilla"><strong>PLANILLA</strong></label>
				</div> 
			</div>
			<div class="row text-center">
				<div class="form-check form-switch col-md-4" style="display: ${style}">
					<input class="form-check-input check-options" type="checkbox" id="checkDeuda" name="checkDeuda" value="Faltante">
					<label class="form-check-label" for="checkDeuda"><strong>F. CAJA</strong></label>
				</div>
				<div class="form-check form-switch col-md-4" style="display: ${style}">
					<input class="form-check-input check-options" type="checkbox" id="checkClientes" name="checkClientes" value="Link">
					<label class="form-check-label" for="checkClientes"><strong>CLIENTES</strong></label>
				</div> 
				<div class="form-check form-switch col-md-4" style="display: ${style}">
					<input class="form-check-input check-options" type="checkbox" id="checkLiquidaciones" name="checkLiquidaciones" value="Liquidaciones">
					<label class="form-check-label" for="checkLiquidaciones"><strong>LIQUIDACIONES</strong></label>
				</div>
			</div>
		`

		this.wrapper.append(
			`<section class="payment-container">
				<div class="section-label payment-section">Método de Pago</div>
				<div class="form-test">
					<div class="card" id="formPinpad">
						<div class="card-body">
							${html_options}
						</div>
					</div>
					<div style="margin-top:50px">					
            			<div id="form-comprobante">
							<div class="form-group mb-3" id="cmpoFactura">
								<label for="factura">¿Deseo emitir factura?</label>
								<input type="checkbox" id="checkFactura"/>
							</div>
							<div class="card" style="width: 100%">
								<div class="card-body">
									<form id="POS" action="#" method="post">
										<div class="form-group section-boleta mb-5">
											<label for=""></label>
											<select class="form-control" id="cmboDoc">
												<option value="dni" selected>DNI</option>
												<option value="ce">Carnet de Extranjeria</option>
											</select>
										</div><br>
										<div class="form-group section-boleta">
											<input type="text" name=""  class="form-control numericOnly" id="cmpoDni" onKeypress="if (event.keyCode < 45 || event.keyCode > 57) event.returnValue = false;" placeholder="Ingrese Documento">
										</div><br>
										<div class="form-group section-boleta">
											<input type="text" name="" id="nom" class="form-control" placeholder="Ingrese Nombre Completo" style="display:none">
										</div>
										<div class="form-group section-factura" style="display:none">
											<input type="text" name="" id="cmpoRuc" class="form-control numericOnly" onKeypress="if (event.keyCode < 45 || event.keyCode > 57) event.returnValue = false;" placeholder="Ingrese ruc">
										</div><br>
										<div class="form-group section-factura" style="display:none">
											<input type="text" name="" id="razonSocial" class="form-control" placeholder="Ingrese Razon Social" style="display:none">
										</div><br>
										<div class="form-group section-factura" style="display:none">
											<input type="text" name="" id="dir" class="form-control" placeholder="Ingrese Direccion" style="display:none">
										</div>
									</form>
								</div>
							</div>
						</div>
					</div>	
				</div>
				<div class="payment-modes" style="display: none"></div>
				<div class="fields-numpad-container" style="display: none">
					<div class="fields-section">
						<div class="section-label">Additional Information</div>
						<div class="invoice-fields"></div>
					</div>
					<div class="number-pad"></div>
				</div>
				<div class="totals-section">
					<div class="totals" style="display: none"></div>
				</div>
				<div class="submit-order-btn">Completar Orden</div>
			</section>`
		);
		this.$component = this.wrapper.find('.payment-container');
		this.$payment_modes = this.$component.find('.payment-modes');
		this.$form_test = this.$component.find('.form-test');
		this.$totals_section = this.$component.find('.totals-section');
		this.$totals = this.$component.find('.totals');
		this.$numpad = this.$component.find('.number-pad');
		this.$invoice_fields_section = this.$component.find('.fields-section');

		// cur_frm.set_value("status_comprobante","Boleta")
		// cur_frm.refresh_field("status_comprobante")
	}

	make_invoice_fields_control() {
		frappe.db.get_doc("POS Settings", undefined).then((doc) => {
			const fields = doc.invoice_fields;
			if (!fields.length) return;

			this.$invoice_fields = this.$invoice_fields_section.find('.invoice-fields');
			this.$invoice_fields.html('');
			const frm = this.events.get_frm();

			fields.forEach(df => {
				this.$invoice_fields.append(
					`<div class="invoice_detail_field ${df.fieldname}-field" data-fieldname="${df.fieldname}"></div>`
				);
				let df_events = {
					onchange: function() {
						frm.set_value(this.df.fieldname, this.get_value());
					}
				};
				if (df.fieldtype == "Button") {
					df_events = {
						click: function() {
							if (frm.script_manager.has_handlers(df.fieldname, frm.doc.doctype)) {
								frm.script_manager.trigger(df.fieldname, frm.doc.doctype, frm.doc.docname);
							}
						}
					};
				}

				this[`${df.fieldname}_field`] = frappe.ui.form.make_control({
					df: {
						...df,
						...df_events
					},
					parent: this.$invoice_fields.find(`.${df.fieldname}-field`),
					render_input: true,
				});
				this[`${df.fieldname}_field`].set_value(frm.doc[df.fieldname]);
			});
		});
	}

	initialize_numpad() {
		const me = this;
		this.number_pad = new erpnext.PointOfSale.NumberPad({
			wrapper: this.$numpad,
			events: {
				numpad_event: function($btn) {
					me.on_numpad_clicked($btn);
				}
			},
			cols: 3,
			keys: [
				[ 1, 2, 3 ],
				[ 4, 5, 6 ],
				[ 7, 8, 9 ],
				[ '.', 0, 'Delete' ]
			],
		});

		this.numpad_value = '';
	}

	on_numpad_clicked($btn) {
		const button_value = $btn.attr('data-button-value');

		highlight_numpad_btn($btn);
		this.numpad_value = button_value === 'delete' ? this.numpad_value.slice(0, -1) : this.numpad_value + button_value;
		this.selected_mode.$input.get(0).focus();
		this.selected_mode.set_value(this.numpad_value);

		function highlight_numpad_btn($btn) {
			$btn.addClass('shadow-base-inner bg-selected');
			setTimeout(() => {
				$btn.removeClass('shadow-base-inner bg-selected');
			}, 100);
		}
	}

	bind_events() {
		const me = this;
		const qr = document.getElementById("checkQR")
		const pinpad = document.getElementById("checkPinpad")
		const planilla = document.getElementById("checkPlanilla")
		const deuda = document.getElementById("checkDeuda")
		const factura = document.getElementById("checkFactura")
		const clientes = document.getElementById("checkClientes")
		var status_comprobante = "Boleta"

		console.log(qr, pinpad, planilla, deuda, factura, status_comprobante. clientes)

		var options_checked = ["checkQR","checkPlanilla","checkDeuda"]
		var options_formulario = ["checkPinpad","checkClientes","checkLiquidaciones"];
		async function verifyCheckedType(){
			var status_checked = false;
			for(const check of options_checked){
				var verification = $(`#${check}`).is(":checked");
				if(verification){
					status_checked = true;
					break;
				}
			}

			return status_checked;
		}
		this.$form_test.on('change', '.check-options', async function (e) {
			var check = $(this).is(":checked");
			var type = e.target.name;
			var type_payment = $(this).val();
			var display = options_formulario.includes(type) ? "none" : "block";
			$(".check-options").prop("checked", false);
			console.error("check",check, e.target.name)
			console.error("type",type)
			console.error("display",display)
			if (check) {
				$(this).prop("checked", true);
				$("#form-comprobante").css("display", display);
			}else{
				$("#form-comprobante").css("display", "block");
				$("#checkFactura").change()
			}

			cur_frm.set_value("status_comprobante",type_payment)
			cur_frm.refresh_field("status_comprobante")
		})
		this.$form_test.on('change', '#checkFactura', async function (e) {
			var check = $(this).is(":checked");
			var obtain_status = await verifyCheckedType();
			console.error("check",obtain_status)
			$(".inputForm").val("");
			if (check) {
				$(this).prop("checked", true);
				$(".section-factura").css("display","block")
				$(".section-boleta").css("display","none")
				var type_payment = !obtain_status ? "Factura":cur_frm.doc.status_comprobante ;
			}else{
				$(".section-boleta").css("display","block")
				$(".section-factura").css("display","none")
				var type_payment = !obtain_status? "Boleta":cur_frm.doc.status_comprobante ;
			}
			cur_frm.set_value("status_comprobante",type_payment)
			cur_frm.refresh_field("status_comprobante")
		})

		this.$form_test.on('keyup', '#cmpoRuc', async function(e) {
			let ruc = $("#cmpoRuc").val();
			cur_frm.set_value("razon_social","")
			cur_frm.set_value("documento","")
			cur_frm.set_value("direccion","")

			if (ruc.length == 11) {
				$(this).blur();
				const resultRuc = await $.ajax({
					type: "post",
					url:"https://syslima.shalomcontrol.com/android/search_persona_store",
					data:{
						"document":ruc
					},
					dataType:"JSON"
				}).fail( function( jqXHR, textStatus, errorThrown ) {
					$("#razonSocial").show();
					$("#dir").show();
					frappe.show_alert({
						message:__("Error del servidor. Digitar la razon social y la direccion de manera manual"),
						indicator:'red'
					}, 5);
				});
				if (resultRuc.valor) {
					$("#razonSocial").show();
					$("#dir").show();
					$("#razonSocial").val(resultRuc.name);
					$("#dir").val(resultRuc.direccion);
					cur_frm.set_value("razon_social",resultRuc.name)
					cur_frm.set_value("documento",ruc)
					cur_frm.set_value("direccion",resultRuc.direccion)
					cur_frm.refresh_field("razon_social")
					cur_frm.refresh_field("documento")
					cur_frm.refresh_field("direccion")

				} else {
					cur_frm.set_value("documento",ruc)
					cur_frm.refresh_field("documento")
					if (!$("#msg").length > 0) {
						$("#cmpoRuc").after("<span id='msg' style='color:red;'>No existe registro en reniec. Digitar la razon social y la direccion de manera manual</span>");
						$("#razonSocial").show();
						$("#dir").show();
					} else {
						frappe.show_alert({
							message:__("No existe registro en reniec. Digitar la razon social y la direccion de manera manual"),
							indicator:'red'
						}, 5);
						$("#razonSocial").val("");
						$("#dir").val("");
						$("#msg").show();
						$("#razonSocial").show();
						$("#dir").show();
					}
				}
			} else {
				cur_frm.set_value("documento",ruc)
				cur_frm.refresh_field("documento")
				$("#msg").hide();
				$("#razonSocial").val("");
				$("#razonSocial").hide();
				$("#dir").val("");
				$("#dir").hide();
			}
		})
		this.$form_test.on('keyup', '#cmpoDni', async function(e) {
			let dni = $(this).val();
			let opc = $("#cmboDoc").val();
			cur_frm.set_value("razon_social","")
			cur_frm.set_value("documento","")
			cur_frm.set_value("direccion","")
			if (dni.length == 8 && opc == "dni") {
				$(this).blur();
				const result_dni = await $.ajax({
					type: "post",
					url:"https://syslima.shalomcontrol.com/android/search_persona_store",
					data:{
						"document":dni
					},
					dataType:"JSON"
				}).fail( function( jqXHR, textStatus, errorThrown ) {
					$("#nom").show();

					cur_frm.set_value("documento",dni)
					cur_frm.refresh_field("documento")
					frappe.show_alert({
						message:__("Error del servidor. Digitar el nombre completo de manera manual"),
						indicator:'red'
					}, 5);

					$("#cmpoDni").after("<span id='msg' style='color:red;'>No existe este registro en reniec. Digitar el nombre completo de manera manual</span>");
				});
				console.log(result_dni, 'result_dni')
				if (result_dni.valor) {
					$("#nom").show();
					$("#nom").val(result_dni.name);
					cur_frm.set_value("razon_social",result_dni.name)
					cur_frm.set_value("documento",dni)
					cur_frm.refresh_field("razon_social")
					cur_frm.refresh_field("documento")
				}else{
					$("#nom").show();
					$("#nom").val(result_dni.name);
					cur_frm.set_value("razon_social",result_dni.name)
					cur_frm.set_value("documento",dni)
					cur_frm.refresh_field("razon_social")
					cur_frm.refresh_field("documento")
					frappe.show_alert({
						message:__("No existe este registro en reniec. Digitar el nombre completo de manera manual"),
						indicator:'red'
					}, 5);
					$("#cmpoDni").after("<span id='msg' style='color:red;'>No existe este registro en reniec. Digitar el nombre completo de manera manual</span>");
				}
			}else if(dni.length == 9 && opc == "ce"){
				cur_frm.set_value("documento",dni)
				cur_frm.refresh_field("documento")
				$("#msg").hide();
				$("#nom").val("");
				$("#nom").show();
			}else{

				cur_frm.set_value("documento", dni)
				cur_frm.refresh_field("documento")
				$("#msg").hide();
				$("#nom").hide();
			}
		})
		this.$form_test.on('keyup', '#nom', async function(e) {
			cur_frm.set_value("razon_social",$(this).val())
		})
		this.$form_test.on('keyup', '#razonSocial', async function(e) {
			cur_frm.set_value("razon_social",$(this).val())
		})
		this.$form_test.on('keyup', '#dir', async function(e) {
			cur_frm.set_value("direccion",$(this).val())
		})
		this.$payment_modes.on('click', '.mode-of-payment', function(e) {
			const mode_clicked = $(this);
			// if clicked element doesn't have .mode-of-payment class then return
			if (!$(e.target).is(mode_clicked)) return;

			const scrollLeft = mode_clicked.offset().left - me.$payment_modes.offset().left + me.$payment_modes.scrollLeft();
			me.$payment_modes.animate({ scrollLeft });

			const mode = mode_clicked.attr('data-mode');

			// hide all control fields and shortcuts
			$(`.mode-of-payment-control`).css('display', 'none');
			$(`.cash-shortcuts`).css('display', 'none');
			me.$payment_modes.find(`.pay-amount`).css('display', 'inline');
			me.$payment_modes.find(`.loyalty-amount-name`).css('display', 'none');

			// remove highlight from all mode-of-payments
			$('.mode-of-payment').removeClass('border-primary');

			if (mode_clicked.hasClass('border-primary')) {
				// clicked one is selected then unselect it
				mode_clicked.removeClass('border-primary');
				me.selected_mode = '';
			} else {
				// clicked one is not selected then select it
				mode_clicked.addClass('border-primary');
				mode_clicked.find('.mode-of-payment-control').css('display', 'flex');
				mode_clicked.find('.cash-shortcuts').css('display', 'grid');
				me.$payment_modes.find(`.${mode}-amount`).css('display', 'none');
				me.$payment_modes.find(`.${mode}-name`).css('display', 'inline');

				me.selected_mode = me[`${mode}_control`];
				me.selected_mode && me.selected_mode.$input.get(0).focus();
				me.auto_set_remaining_amount();
			}
		});

		frappe.ui.form.on('POS Invoice', 'contact_mobile', (frm) => {
			const contact = frm.doc.contact_mobile;
			const request_button = $(this.request_for_payment_field.$input[0]);
			if (contact) {
				request_button.removeClass('btn-default').addClass('btn-primary');
			} else {
				request_button.removeClass('btn-primary').addClass('btn-default');
			}
		});

		this.setup_listener_for_payments();

		this.$payment_modes.on('click', '.shortcut', function() {
			const value = $(this).attr('data-value');
			me.selected_mode.set_value(value);
		});

		const _this = this

		this.$component.on('click', '.submit-order-btn', async function (){
			$(this).attr("disabled",true);
			const frm = _this.events.get_frm();
			const doc = _this.events.get_frm().doc;
			const paid_amount = cur_frm.doc.paid_amount;
			const items = cur_frm.doc.items;

			const tipo_comprobante = cur_frm.doc.status_comprobante

			console.log(tipo_comprobante)
			console.log(cur_frm.doc.documento, 'documento arriba')
			const documento = cur_frm.doc.documento ? cur_frm.doc.documento: ""
			const razon_social = cur_frm.doc.razon_social ? cur_frm.doc.razon_social : ""
			const direccion = cur_frm.doc.direccion ? cur_frm.doc.direccion : ""
			let opc = $("#cmboDoc").val();
			let checkFactura = $("#checkFactura").is(':checked');

			if (tipo_comprobante == "Planilla" && documento.length == 11) {

				frappe.throw(__('Para el pago de planilla solo se permite boletas'));
				return false;

			}

			if (tipo_comprobante == "Faltante" && documento.length == 11) {

				frappe.throw(__('Para el faltante de caja solo se permite boletas'));
				return false;

			}

			if (!["Link","Pago por PINPAD","Liquidaciones"].includes(tipo_comprobante)) {

				if (documento.length == 11 && razon_social == "" && direccion == "" && documento == "") {

					frappe.throw(__('El documento, razon social y direccion son obligatorios'));
					return false;

				}

				if (documento.length != 11 && razon_social == "" && documento == "") {

					frappe.throw(__('El documento y razon social son obligatorios'));
					return false;

				}

				if ( !documento || documento == "") {

					frappe.throw(__('El documento es obligatorio'));
					return false;

				}

				if( documento.length != 8 && opc == "dni" && checkFactura == false  ){
					frappe.throw(__('El número de DNI debe ser de 8 dígitos'));
					return false;
				}

				if( documento.length != 9 && opc == "ce" && checkFactura == false ){
					frappe.throw(__('El número de CE debe ser de 9 dígitos'));
					return false;
				}

				if( documento.length != 11 && checkFactura == true ){
					frappe.throw(__('El número de ruc debe ser de 11 dígitos'));
					return false;
				}

			}


			if (paid_amount == 0 || !items.length) {
				const message = items.length ? __("You cannot submit the order without payment.") : __("You cannot submit empty order.");
				frappe.show_alert({ message, indicator: "orange" });
				frappe.utils.play_sound("error");
				return;
			}

			let count_packaging = 0;

			for (const item of items) {
				if(item.item_code.substring(0,6) == "SEREMB"){
					count_packaging++;
				}
			}
			if(count_packaging > 0){
				if(items.length != count_packaging){

					cur_frm.set_value("update_stock",1);
					cur_frm.set_value("tipo_de_venta","Embalaje y Tienda");

				}else{

					cur_frm.set_value("update_stock",1);
					cur_frm.set_value("tipo_de_venta","Embalaje");

				}
			}

			if(["Faltante","Planilla"].includes(tipo_comprobante)){

				const months = [
					"Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio",
					"Agosto","Setiembre","Octubre","Noviembre","Diciembre"
				]

				console.log('cur_frm.doc.documento', cur_frm.doc.documento)
				console.log('documento', documento)
				const service_employee = await $.ajax({
					"url":"https://recursoshumanos.shalom.com.pe/api/get-employee-by-documento",
					"type":"POST",
					"data":{
						documento:documento
					}
				})
				console.log("service_employee", service_employee)
				if(!service_employee.valor){

					frappe.throw(__('Para el faltante de caja solo empleados de shalom'));
					return false;

				}

				var amount_letras = await $.ajax({
					type:"POST",
					url:"https://syslima.shalomcontrol.com/api/numtoletras",
					data:{
						"xcifra" : cur_frm.doc.grand_total
					},
				})

				amount_letras = amount_letras.toLowerCase();

				const motivo = {
					"Faltante":"FALTANTE DE CAJA DE SHALOM STORE",
					"Planilla":"VENTA DE MERCHANDISING"
				}

				const insert = await frappe.db.insert({

					doctype:"Reconociemientos de Deuda",
					empleado:service_employee.data.name,
					motivo: motivo[tipo_comprobante],
					monto_total:cur_frm.doc.grand_total,
					table_21: [

						{
							mes:months[moment(new Date()).month()],
							monto:cur_frm.doc.grand_total,
							ano: moment(new Date()).year()

						}

					],
					monto_en_texto: amount_letras
				})

			}

			_this.events.submit_invoice();




			$(this).attr("disabled",false);

		});

		frappe.ui.form.on('POS Invoice', 'paid_amount', (frm) => {
			this.update_totals_section(frm.doc);

			// need to re calculate cash shortcuts after discount is applied
			const is_cash_shortcuts_invisible = !this.$payment_modes.find('.cash-shortcuts').is(':visible');
			this.attach_cash_shortcuts(frm.doc);
			!is_cash_shortcuts_invisible && this.$payment_modes.find('.cash-shortcuts').css('display', 'grid');
		});

		frappe.ui.form.on('POS Invoice', 'loyalty_amount', (frm) => {
			const formatted_currency = format_currency(frm.doc.loyalty_amount, frm.doc.currency);
			this.$payment_modes.find(`.loyalty-amount-amount`).html(formatted_currency);
		});

		frappe.ui.form.on("Sales Invoice Payment", "amount", (frm, cdt, cdn) => {
			// for setting correct amount after loyalty points are redeemed
			const default_mop = locals[cdt][cdn];
			const mode = default_mop.mode_of_payment.replace(/ +/g, "_").toLowerCase();
			if (this[`${mode}_control`] && this[`${mode}_control`].get_value() != default_mop.amount) {
				this[`${mode}_control`].set_value(default_mop.amount);
			}
		});
	}

	setup_listener_for_payments() {
		frappe.realtime.on("process_phone_payment", (data) => {
			const doc = this.events.get_frm().doc;
			const { response, amount, success, failure_message } = data;
			let message, title;

			if (success) {
				title = __("Payment Received");
				const grand_total = cint(frappe.sys_defaults.disable_rounded_total) ? doc.grand_total : doc.rounded_total;
				if (amount >= grand_total) {
					frappe.dom.unfreeze();
					message = __("Payment of {0} received successfully.", [format_currency(amount, doc.currency, 0)]);
					this.events.submit_invoice();
					cur_frm.reload_doc();

				} else {
					message = __("Payment of {0} received successfully. Waiting for other requests to complete...", [format_currency(amount, doc.currency, 0)]);
				}
			} else if (failure_message) {
				message = failure_message;
				title = __("Payment Failed");
			}

			frappe.msgprint({ "message": message, "title": title });
		});
	}

	auto_set_remaining_amount() {
		const doc = this.events.get_frm().doc;
		const grand_total = cint(frappe.sys_defaults.disable_rounded_total) ? doc.grand_total : doc.rounded_total;
		const remaining_amount = grand_total - doc.paid_amount;
		const current_value = this.selected_mode ? this.selected_mode.get_value() : undefined;
		if (!current_value && remaining_amount > 0 && this.selected_mode) {
			this.selected_mode.set_value(remaining_amount);
		}
	}

	setup_listener_for_payments() {
		frappe.realtime.on("process_phone_payment", (data) => {
			const doc = this.events.get_frm().doc;
			const { response, amount, success, failure_message } = data;
			let message, title;

			if (success) {
				title = __("Payment Received");
				if (amount >= doc.grand_total) {
					frappe.dom.unfreeze();
					message = __("Payment of {0} received successfully.", [format_currency(amount, doc.currency, 0)]);
					this.events.submit_invoice();
					cur_frm.reload_doc();

				} else {
					message = __("Payment of {0} received successfully. Waiting for other requests to complete...", [format_currency(amount, doc.currency, 0)]);
				}
			} else if (failure_message) {
				message = failure_message;
				title = __("Payment Failed");
			}

			frappe.msgprint({ "message": message, "title": title });
		});
	}

	auto_set_remaining_amount() {
		const doc = this.events.get_frm().doc;
		const remaining_amount = doc.grand_total - doc.paid_amount;
		const current_value = this.selected_mode ? this.selected_mode.get_value() : undefined;
		if (!current_value && remaining_amount > 0 && this.selected_mode) {
			this.selected_mode.set_value(remaining_amount);
		}
	}

	attach_shortcuts() {
		const ctrl_label = frappe.utils.is_mac() ? '⌘' : 'Ctrl';
		this.$component.find('.submit-order-btn').attr("title", `${ctrl_label}+Enter`);
		frappe.ui.keys.on("ctrl+enter", () => {
			const payment_is_visible = this.$component.is(":visible");
			const active_mode = this.$payment_modes.find(".border-primary");
			if (payment_is_visible && active_mode.length) {
				this.$component.find('.submit-order-btn').click();
			}
		});

		frappe.ui.keys.add_shortcut({
			shortcut: "tab",
			action: () => {
				const payment_is_visible = this.$component.is(":visible");
				let active_mode = this.$payment_modes.find(".border-primary");
				active_mode = active_mode.length ? active_mode.attr("data-mode") : undefined;

				if (!active_mode) return;

				const mode_of_payments = Array.from(this.$payment_modes.find(".mode-of-payment")).map(m => $(m).attr("data-mode"));
				const mode_index = mode_of_payments.indexOf(active_mode);
				const next_mode_index = (mode_index + 1) % mode_of_payments.length;
				const next_mode_to_be_clicked = this.$payment_modes.find(`.mode-of-payment[data-mode="${mode_of_payments[next_mode_index]}"]`);

				if (payment_is_visible && mode_index != next_mode_index) {
					next_mode_to_be_clicked.click();
				}
			},
			condition: () => this.$component.is(':visible') && this.$payment_modes.find(".border-primary").length,
			description: __("Switch Between Payment Modes"),
			ignore_inputs: true,
			page: cur_page.page.page
		});
	}

	toggle_numpad() {
		// pass
	}

	render_payment_section() {
		this.render_payment_mode_dom();
		this.make_invoice_fields_control();
		this.update_totals_section();
	}

	edit_cart() {
		this.events.toggle_other_sections(false);
		this.toggle_component(false);
	}

	checkout() {
		this.events.toggle_other_sections(true);
		this.toggle_component(true);

		this.render_payment_section();
	}

	toggle_remarks_control() {
		if (this.$remarks.find('.frappe-control').length) {
			this.$remarks.html('+ Add Remark');
		} else {
			this.$remarks.html('');
			this[`remark_control`] = frappe.ui.form.make_control({
				df: {
					label: __('Remark'),
					fieldtype: 'Data',
					onchange: function() {}
				},
				parent: this.$totals_section.find(`.remarks`),
				render_input: true,
			});
			this[`remark_control`].set_value('');
		}
	}

	render_payment_mode_dom() {
		const doc = this.events.get_frm().doc;
		const payments = doc.payments;
		const currency = doc.currency;

		this.$payment_modes.html(`${
			payments.map((p, i) => {
				const mode = p.mode_of_payment.replace(/ +/g, "_").toLowerCase();
				const payment_type = p.type;
				const margin = i % 2 === 0 ? 'pr-2' : 'pl-2';
				const amount = p.amount > 0 ? format_currency(p.amount, currency) : '';

				return (`
					<div class="payment-mode-wrapper">
						<div class="mode-of-payment" data-mode="${mode}" data-payment-type="${payment_type}">
							${p.mode_of_payment}
							<div class="${mode}-amount pay-amount">${amount}</div>
							<div class="${mode} mode-of-payment-control"></div>
						</div>
					</div>
				`);
			}).join('')
		}`);

		payments.forEach(p => {
			const mode = p.mode_of_payment.replace(/ +/g, "_").toLowerCase();
			const me = this;
			this[`${mode}_control`] = frappe.ui.form.make_control({
				df: {
					label: p.mode_of_payment,
					fieldtype: 'Currency',
					placeholder: __('Enter {0} amount.', [p.mode_of_payment]),
					onchange: function() {
						const current_value = frappe.model.get_value(p.doctype, p.name, 'amount');
						if (current_value != this.value) {
							frappe.model
								.set_value(p.doctype, p.name, 'amount', flt(this.value))
								.then(() => me.update_totals_section())

							const formatted_currency = format_currency(this.value, currency);
							me.$payment_modes.find(`.${mode}-amount`).html(formatted_currency);
						}
					}
				},
				parent: this.$payment_modes.find(`.${mode}.mode-of-payment-control`),
				render_input: true,
			});
			this[`${mode}_control`].toggle_label(false);
			this[`${mode}_control`].set_value(p.amount);

			if (p.default) {
				setTimeout(() => {
					this.$payment_modes.find(`.${mode}.mode-of-payment-control`).parent().click();
				}, 500);
			}
		});

		this.render_loyalty_points_payment_mode();

		this.attach_cash_shortcuts(doc);
	}

	attach_cash_shortcuts(doc) {
		const grand_total = cint(frappe.sys_defaults.disable_rounded_total) ? doc.grand_total : doc.rounded_total;
		const currency = doc.currency;

		const shortcuts = this.get_cash_shortcuts(flt(grand_total));

		this.$payment_modes.find('.cash-shortcuts').remove();
		let shortcuts_html = shortcuts.map(s => {
			return `<div class="shortcut" data-value="${s}">${format_currency(s, currency, 0)}</div>`;
		}).join('');

		this.$payment_modes.find('[data-payment-type="Cash"]').find('.mode-of-payment-control')
			.after(`<div class="cash-shortcuts">${shortcuts_html}</div>`);
	}

	get_cash_shortcuts(grand_total) {
		let steps = [1, 5, 10];
		const digits = String(Math.round(grand_total)).length;

		steps = steps.map(x => x * (10 ** (digits - 2)));

		const get_nearest = (amount, x) => {
			let nearest_x = Math.ceil((amount / x)) * x;
			return nearest_x === amount ? nearest_x + x : nearest_x;
		};

		return steps.reduce((finalArr, x) => {
			let nearest_x = get_nearest(grand_total, x);
			nearest_x = finalArr.indexOf(nearest_x) != -1 ? nearest_x + x : nearest_x;
			return [...finalArr, nearest_x];
		}, []);
	}

	render_loyalty_points_payment_mode() {
		const me = this;
		const doc = this.events.get_frm().doc;
		const { loyalty_program, loyalty_points, conversion_factor } = this.events.get_customer_details();

		this.$payment_modes.find(`.mode-of-payment[data-mode="loyalty-amount"]`).parent().remove();

		if (!loyalty_program) return;

		let description, read_only, max_redeemable_amount;
		if (!loyalty_points) {
			description = __("You don't have enough points to redeem.");
			read_only = true;
		} else {
			max_redeemable_amount = flt(flt(loyalty_points) * flt(conversion_factor), precision("loyalty_amount", doc));
			description = __("You can redeem upto {0}.", [format_currency(max_redeemable_amount)]);
			read_only = false;
		}

		const margin = this.$payment_modes.children().length % 2 === 0 ? 'pr-2' : 'pl-2';
		const amount = doc.loyalty_amount > 0 ? format_currency(doc.loyalty_amount, doc.currency) : '';
		this.$payment_modes.append(
			`<div class="payment-mode-wrapper">
				<div class="mode-of-payment loyalty-card" data-mode="loyalty-amount" data-payment-type="loyalty-amount">
					Redeem Loyalty Points
					<div class="loyalty-amount-amount pay-amount">${amount}</div>
					<div class="loyalty-amount-name">${loyalty_program}</div>
					<div class="loyalty-amount mode-of-payment-control"></div>
				</div>
			</div>`
		);

		this['loyalty-amount_control'] = frappe.ui.form.make_control({
			df: {
				label: __("Redeem Loyalty Points"),
				fieldtype: 'Currency',
				placeholder: __("Enter amount to be redeemed."),
				options: 'company:currency',
				read_only,
				onchange: async function() {
					if (!loyalty_points) return;

					if (this.value > max_redeemable_amount) {
						frappe.show_alert({
							message: __("You cannot redeem more than {0}.", [format_currency(max_redeemable_amount)]),
							indicator: "red"
						});
						frappe.utils.play_sound("submit");
						me['loyalty-amount_control'].set_value(0);
						return;
					}
					const redeem_loyalty_points = this.value > 0 ? 1 : 0;
					await frappe.model.set_value(doc.doctype, doc.name, 'redeem_loyalty_points', redeem_loyalty_points);
					frappe.model.set_value(doc.doctype, doc.name, 'loyalty_points', parseInt(this.value / conversion_factor));
				},
				description
			},
			parent: this.$payment_modes.find(`.loyalty-amount.mode-of-payment-control`),
			render_input: true,
		});
		this['loyalty-amount_control'].toggle_label(false);

		// this.render_add_payment_method_dom();
	}

	render_add_payment_method_dom() {
		const docstatus = this.events.get_frm().doc.docstatus;
		if (docstatus === 0)
			this.$payment_modes.append(
				`<div class="w-full pr-2">
					<div class="add-mode-of-payment w-half text-grey mb-4 no-select pointer">+ Add Payment Method</div>
				</div>`
			);
	}

	update_totals_section(doc) {
		if (!doc) doc = this.events.get_frm().doc;
		const paid_amount = doc.paid_amount;
		const grand_total = cint(frappe.sys_defaults.disable_rounded_total) ? doc.grand_total : doc.rounded_total;
		const remaining = grand_total - doc.paid_amount;
		const change = doc.change_amount || remaining <= 0 ? -1 * remaining : undefined;
		const currency = doc.currency;
		const label = change ? __('Change') : __('To Be Paid');

		this.$totals.html(
			`<div class="col">
				<div class="total-label">Total</div>
				<div class="value">${format_currency(grand_total, currency)}</div>
			</div>
			<div class="seperator-y"></div>
			<div class="col">
				<div class="total-label">Monto de Pago</div>
				<div class="value">${format_currency(paid_amount, currency)}</div>
			</div>
			<div class="seperator-y"></div>
			<div class="col">
				<div class="total-label">${label}</div>
				<div class="value">${format_currency(change || remaining, currency)}</div>
			</div>`
		);
	}

	toggle_component(show) {
		show ? this.$component.css('display', 'flex') : this.$component.css('display', 'none');
	}
};
