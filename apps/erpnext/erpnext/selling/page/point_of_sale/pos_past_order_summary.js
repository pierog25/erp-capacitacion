async function makeIdentifier(length) {
	let idc = await $.ajax({
		url: "https://newpadawan.shalomcontrol.com/android/insert_niubiz_correlativo",
		type: "post",
	})
	var parseidc = JSON.parse(idc);
	return zfill(parseidc,length);
}
function alertLoading(time){
	frappe.show_progress('Espera mientras se verifica el pago y se genera el comprobante.', time, 100, 'Espere por favor');
}

function zfill(number, width) {
	var numberOutput = Math.abs(number); /* Valor absoluto del número */
	var length = number.toString().length; /* Largo del número */
	var zero = "0"; /* String de cero */

	if (width <= length) {
		if (number < 0) {
			return ("-" + numberOutput.toString());
		} else {
			return numberOutput.toString();
		}
	} else {
		if (number < 0) {
			return ("-" + (zero.repeat(width - length)) + numberOutput.toString());
		} else {
			return ((zero.repeat(width - length)) + numberOutput.toString());
		}
	}
}
erpnext.PointOfSale.PastOrderSummary = class {
	constructor({ wrapper, events }) {
		this.wrapper = wrapper;
		this.events = events;

		this.init_component();
	}

	init_component() {
		this.prepare_dom();
		this.init_email_print_dialog();
		this.bind_events();
		this.attach_shortcuts();
	}

	prepare_dom() {
		this.wrapper.append(
			`<section class="past-order-summary">
				<div class="no-summary-placeholder">
					Select an invoice to load summary data
				</div>
				<div class="invoice-summary-wrapper">
					<div class="abs-container">
						<div class="upper-section"></div>
						<div class="label section-qr titulo-qr" style="display: none">Generar QR</div>
						<div class="section-qr div-qr" style="display: none"></div>
						<div class="label">Productos</div>
						<div class="items-container summary-container"></div>
						<div class="label">Pagos</div>
						<div class="totals-container summary-container"></div>
						<div class="label" style="display: none">Pagos</div>
						<div class="payments-container summary-container" style="display: none"></div>
						<div class="summary-btns"></div>
					</div>
				</div>
			</section>`
		);

		this.$component = this.wrapper.find('.past-order-summary');
		this.$summary_wrapper = this.$component.find('.invoice-summary-wrapper');
		this.$summary_container = this.$component.find('.abs-container');
		this.$upper_section = this.$summary_container.find('.upper-section');
		this.$items_container = this.$summary_container.find('.items-container');
		this.$totals_container = this.$summary_container.find('.totals-container');
		this.$payment_container = this.$summary_container.find('.payments-container');
		this.$summary_btns = this.$summary_container.find('.summary-btns');
		this.$payment_niubiz = this.$summary_container.find('.div-qr');
	}

	init_email_print_dialog() {
		const email_dialog = new frappe.ui.Dialog({
			title: 'Email Receipt',
			fields: [
				{fieldname: 'email_id', fieldtype: 'Data', options: 'Email', label: 'Email ID'},
				// {fieldname:'remarks', fieldtype:'Text', label:'Remarks (if any)'}
			],
			primary_action: () => {
			this.send_email();
	},
		primary_action_label: __('Send'),
	});
		this.email_dialog = email_dialog;

		const print_dialog = new frappe.ui.Dialog({
			title: 'Print Receipt',
			fields: [
				{fieldname: 'print', fieldtype: 'Data', label: 'Print Preview'}
			],
			primary_action: () => {
			this.print_receipt();
	},
		primary_action_label: __('Print'),
	});
		this.print_dialog = print_dialog;
	}

	get_upper_section_html(doc) {
		const { status } = doc;
		let indicator_color = '';
		in_list(['Paid', 'Consolidated'], status) && (indicator_color = 'green');
		status === 'Draft' && (indicator_color = 'red');
		status === 'Return' && (indicator_color = 'grey');

		console.log(doc)

		let apartQR = doc.status_comprobante == "QR" ? `
			<div class="mb-2">
				<div class="form-genera-qr form-group">
					<button type="button" class="btn btn-sm btn-danger btn-block form-control" id="generate_payment">Generar QR</button>
					<button type="button" class="btn btn-sm btn-primary btn-block form-control" data-idc="" data-guias="" id="generate_comprobant" style="display: none">Generar Comprobante</button>
				 </div>
			</div>`:''
		if(doc.status_comprobante == "QR"){

			$(".div-qr").html(apartQR);
			$(".section-qr").css("display","block");
			$(".titulo-qr").html("Generar QR");

		}else{

			if(doc.comprobante){

				$(".div-qr").html(`
                     <div style='margin-bottom: 10px;'>
                        <div class='card' id='cardEnlace' border-color:black><div class='card-body'>
                            <span>Para ver el comprobante 
                                <a href=${doc.link_factura} target='_blank' text-white >
                                    <font color="black"><strong><u>clickea aqui<u></strong></font>
                                </a>
                            </span>
                        </div>
                    </div>
				
				`);
				$(".titulo-qr").html("Comprobante");
				$(".section-qr").css("display","block");

			}else{
				$(".div-qr").html(``)
				$(".section-qr").css("display","none");

			}

		}
		return `<div class="left-section">
					<div class="customer-name">${doc.customer}</div>
					<div class="customer-email">${this.customer_email}</div>
					<div class="cashier">Vendido por: ${doc.owner}</div>
				</div>
				<div class="right-section">
					<div class="paid-amount">${format_currency(doc.grand_total, doc.currency)}</div>
					<div class="invoice-name">${doc.name}</div>
				</div>`;
	}

	get_item_html(doc, item_data) {
		return `<div class="item-row-wrapper">
					<div class="item-name">${item_data.item_name}</div>
					<div class="item-qty">${item_data.qty || 0}</div>
					<div class="item-rate-disc">${get_rate_discount_html()}</div>
				</div>`;

		function get_rate_discount_html() {
			if (item_data.rate && item_data.price_list_rate && item_data.rate !== item_data.price_list_rate) {
				return `<span class="item-disc">(${item_data.discount_percentage}% off)</span>
						<div class="item-rate">${format_currency(item_data.rate, doc.currency)}</div>`;
			} else {
				return `<div class="item-rate">${format_currency(item_data.price_list_rate || item_data.rate, doc.currency)}</div>`;
			}
		}
	}

	get_discount_html(doc) {
		if (doc.discount_amount) {
			return `<div class="summary-row-wrapper">
						<div>Descuento</div>
						<div>${format_currency(doc.discount_amount, doc.currency)}</div>
					</div>`;
		} else {
			return ``;
		}
	}

	get_net_total_html(doc) {
		return `<div class="summary-row-wrapper" style="display: none">
					<div>Total Neto</div>
					<div>${format_currency(doc.net_total, doc.currency)}</div>
				</div>`;
	}

	get_taxes_html(doc) {
		if (!doc.taxes.length) return '';

		let taxes_html = doc.taxes.map(t => {
			const description = /[0-9]+/.test(t.description) ? t.description : `${t.description} @ ${t.rate}%`;
		return `
				<div class="tax-row">
					<div class="tax-label">${description}</div>
					<div class="tax-value">${format_currency(t.tax_amount_after_discount_amount, doc.currency)}</div>
				</div>
			`;
	}).join('');

		return `<div class="taxes-wrapper">${taxes_html}</div>`;
	}

	get_grand_total_html(doc) {
		return `<div class="summary-row-wrapper grand-total">
					<div>Pago</div>
					<div>${format_currency(doc.grand_total, doc.currency)}</div>
				</div>`;
	}

	get_payment_html(doc, payment) {
		return `<div class="summary-row-wrapper payments">
					<div>${payment.mode_of_payment}</div>
					<div>${format_currency(payment.amount, doc.currency)}</div>
				</div>`;
	}

	bind_events() {
		this.$summary_container.on('click', '.return-btn', () => {
			this.events.process_return(this.doc.name);
		this.toggle_component(false);
		this.$component.find('.no-summary-placeholder').css('display', 'flex');
		this.$summary_wrapper.css('display', 'none');
	});
		const _this = this

		this.$payment_niubiz.on('click', '#generate_payment', async function () {
			let btn_genera = document.getElementById("generate_comprobant");
			const niubizQR = new niubizOverskull();
			var facturas = [_this.doc.name];
			const username = "sistema@shalom.com.pe";
			const password = "nF8_e@$N";
			var guidesStr = '';
			var i;
			for (i = 0 ; i < facturas.length ; i++)
			{
				if(i == (facturas.length - 1)){
					guidesStr += `cdn${(i+1)}:${facturas[i]}#tiendita:1`
				}else{
					guidesStr += `cdn${(i+1)}:${facturas[i]}#`
				}
			}
			let qrfhvencimiento = moment(new Date()).format("YYYY-MM-DD");
			let monto = _this.doc.grand_total
			var fechaVencimiento = qrfhvencimiento;
			var fechaVencimientoDate = new Date(qrfhvencimiento);
			fechaVencimientoDate.setDate(fechaVencimientoDate.getDate() + 2);
			const year = fechaVencimientoDate.getFullYear();
			const month = (fechaVencimientoDate.getMonth() + 1).toString();
			const day = (fechaVencimientoDate.getDate()).toString();
			const resultDaySend = day.padStart(2,"0") + month.padStart(2,"0") + year + ''
			const additionalData = guidesStr;
			const idc = await makeIdentifier(10);
			var amountSend = (Math.round(monto * 100) / 100).toFixed(2);
			const encodeAuth = window.btoa(username+':'+password);
			const responseNiubizTok = await niubizQR.generateTokenNiubiz(encodeAuth);
			if(!responseNiubizTok.value){
				alert("Ocurrio un error al generar Token a Niubiz, vuelva a intentar.");
				return;
			}
			let tokenResponse = responseNiubizTok.data;
			const responseNiubizQR = await niubizQR.generateQRNiubiz(tokenResponse,amountSend,resultDaySend,additionalData,idc);
			if(responseNiubizQR.value){
				const responseGenerateQR = await $.ajax({
					url: 'https://newpadawan.shalomcontrol.com/android/generar_img_qr',
					data: {
						idose: JSON.stringify(facturas),
						fecha_vencimiento: fechaVencimiento,
						idc: idc,
						monto: monto,
						img: responseNiubizQR.data.tagImg,
						id_img: responseNiubizQR.data.tagId,
					},
					type: "post"
				});
				var parseGenerate = responseGenerateQR
				if(parseGenerate.valor){
					cur_frm.doc.idc = idc
					const updateForPos = frappe.db.set_value('POS Invoice',_this.doc.name,{
						'idc':idc
					})
					btn_genera.dataset.idc = idc
					btn_genera.dataset.guias = JSON.stringify(facturas)
					$("#generate_comprobant").css("display","block");
					let msn = `
								<div class="row">
									<div class="col-2">
										<a class="btn btn-primary" id="btnPrintQrNiubizModal"><i class="fa fa-print" aria-hidden="true"></i> Imprimir</a>
									</div>
								</div>
								<div class="row">
									<div class="col-md-2 col-lg-2"></div>
									<div class="col-md-8 col-lg-8">
										<div class="container mr-3">
											<div class="contenedorQR" style="position: relative;width: 300px;height: 300px;margin: 20px;">
												<div class="titulo" style="text-align: center;background-color: white; position: absolute;left: 3.5%;top: -8px;padding: 0 15px 0 15px;font-weight: bold;">ESCANEA Y PAGA TUS VENTAS CON</div>
												<div class="padre" style="height: 265px;width: 300px;border: 1px solid;border-radius: 10px;display: flex;align-items: center;justify-content: center;">
													<div class="qr_container" style="text-align: center;position: relative;">
														<img class="soles" style="width: 35px;position: absolute;top: -27px;left: 44%;"src="https://fileserver.shalomcontrol.com/file-view/images/5m2z2jQha42KhrbW0mBYea691af9-a2c7-4889-bb64-f767e076a2ff.jpg" alt="">
														<div id="generateqr" style="text-align: center;">
															 <img src="${responseNiubizQR.data.tagImg}" style="width: 50%; text-align: center;" alt="scale" class="img_img">
														</div>
													</div>
												</div>
												<div class="imagenes" style="text-align: center;background-color: white;position: absolute;left: 10%;bottom: 15px;padding: 0 15px 0 15px;">
													<img class="img" style=" width: 50px;height: 50px;border-radius: 5px;" src="https://fileserver.shalomcontrol.com/file-view/images/4frEFpj1fr9LKlhhp7GIf31c83d2-6378-432d-990c-7775024102ff.jpg" alt="">
													<img class="img_b" style=" width: 50px;height: 50px;border-radius: 5px;border: solid 1px #c9c3c3;" src="https://fileserver.shalomcontrol.com/file-view/images/ZWXY9Whz4hU8lLXO8Pt5461c2388-a00a-4230-a05f-49eb1a8af1f7.jpg" alt="">
													<img class="img_b" style=" width: 50px;height: 50px;border-radius: 5px;border: solid 1px #c9c3c3;" src="https://fileserver.shalomcontrol.com/file-view/images/Z8Slj0NVdjay56xuJFuT2df6dacf-8431-4700-8f0d-250b4b91da0e.jpg" alt="">
													<img class="img" style=" width: 50px;height: 50px;border-radius: 5px;" src="https://fileserver.shalomcontrol.com/file-view/images/eKoUo4MS8N2ZHBsQY9G3c979c760-b548-4967-a6d8-abeb1901cfc0.jpg" alt="">
												</div>
											</div>
										</div>
									</div>
									<div class="col-md-2 col-lg-2"></div>
								</div>
							`


					frappe.msgprint({
						title: __('QR'),
						indicator: 'green',
						message: (msn)
					});
				}else{
					btn_genera.dataset.idc = ""
					btn_genera.dataset.guias = ""
					$("#generate_comprobant").css("display","block");
					frappe.throw("Ocurrio un error al Generar el QR, vuelva a intentar.");
					return false;
				}
			}
			else{
				const errorGenerateQR = await $.ajax({
					url: 'https://newpadawan.shalomcontrol.com/android/error_img_qr',
					data: {
						idose: facturas,
						data: responseNiubizQR.data,
					},
					type: "post"
				});
				btn_genera.dataset.idc = ""
				$("#generate_comprobant").css("display","block");
				frappe.throw("Ocurrio un error al Generar el QR, vuelva a intentar.");
				return false;
			}
		});

		this.$payment_niubiz.on('click', '#btnPrintQrNiubizModal', async function () {

			console.log(_this, idc_new)

			// const idose = idc_new
			// window.open(`https://empresarial.shalomcontrol.com/pagosPdfBilleteraQR/${idose}`,"_blank");


		})


		this.$payment_niubiz.on('click', '#generate_comprobant',  async function (){
			console.log('es ese? marcos????????')
			alertLoading(10)
			let idc = $("#generate_comprobant").data("idc");
			let guias = $("#generate_comprobant").data("guias");
			let ajaxValidatePayQR = await $.ajax({
				url: 'https://syslima.shalomcontrol.com/api/validate_form_payment',
				data: {
					idc: idc,
					cdn: _this.doc.name
				},
				type: "post",
				dataType:"JSON"
			})
			alertLoading(30)
			if(!ajaxValidatePayQR.valor){
				setTimeout(()=>{
					frappe.cur_progress.hide();
					frappe.cur_progress = null;
				},1000)

				frappe.throw(ajaxValidatePayQR.msg);
				return false;
			}
			console.log('es ese????')
			// let productosData = JSON.parse(localStorage.getItem("itemsnew"))
			let status_comprobante = _this.doc.status_comprobante
			let documento = _this.doc.documento
			let razon_social = _this.doc.razon_social
			let direccion = _this.doc.direccion
			alertLoading(50)
			var datos={};
			var productos = [];
			for(const producto of _this.doc.items){
				productos.push({
					descripcion:producto.description,
					importe:producto.amount,
					precioUnitario:producto.rate,
					cantidad:producto.qty
				});
			}
			let type = ""
			if(direccion == "" || direccion == null || direccion == undefined){
				datos = {
					tipoComprobante:'boleta',
					entidadPaga:documento,
					razonSocial:razon_social,
					productos:productos,
					cdn:_this.doc.name,
					userDni:'70503353',
					medio_pago: 'BILLETERA ELECTRONICA'
				};
			}else{
				datos = {
					tipoComprobante:'factura',
					entidadPaga:documento,
					razonSocial:razon_social,
					productos:productos,
					direccion:direccion,
					cdn:_this.doc.name,
					userDni:'70503353',
					medio_pago: 'BILLETERA ELECTRONICA'
				};
			}
			alertLoading(60)
			console.log('es ese????')
			const registerComp = await $.ajax({
				url:'https://fileserver.shalomcontrol.com/api/registrar-comprobante-erp',
				type:'post',
				data:datos
			}).fail( function( jqXHR, textStatus, errorThrown ) {
				setTimeout(()=>{

					frappe.cur_progress.hide();
				frappe.cur_progress = null;

			},1000)
				frappe.throw(errorThrown);
				return false;
			});

			alertLoading(80)
			if(registerComp.estado){

				setTimeout(()=>{

					frappe.cur_progress.hide();
				frappe.cur_progress = null;

			},1000)

				$(".section-qr").css("display","none");
				window.open(registerComp.enlacepdf,"_blank")
				const updateComp = await frappe.db.set_value('POS Invoice', _this.doc.name, {
					"comprobante":1,
					"serie": registerComp.data.serie,
					"numero":  registerComp.data.numero,
					"link_factura":  registerComp.enlacepdf
				})
				frappe.msgprint({
					title: __('Comprobante Generado'),
					indicator: 'green',
					message: __(registerComp.msn)
				});
			}else{
				setTimeout(()=>{

					frappe.cur_progress.hide();
				frappe.cur_progress = null;

			},1000)
				frappe.msgprint({
					title: __('Error al generar comprobante'),
					indicator: 'red',
					message: __(registerComp.msn)
				});
			}
		})
		this.$summary_container.on('click', '.edit-btn', () => {
			this.events.edit_order(this.doc.name);
		this.toggle_component(false);
		this.$component.find('.no-summary-placeholder').css('display', 'flex');
		this.$summary_wrapper.css('display', 'none');
	});

		this.$summary_container.on('click', '.delete-btn', () => {
			this.events.delete_order(this.doc.name);
		this.show_summary_placeholder();
	});

		this.$summary_container.on('click', '.delete-btn', () => {
			this.events.delete_order(this.doc.name);
		this.show_summary_placeholder();
		// this.toggle_component(false);
		// this.$component.find('.no-summary-placeholder').removeClass('d-none');
		// this.$summary_wrapper.addClass('d-none');
	});

		this.$summary_container.on('click', '.new-btn', () => {
			this.events.new_order();
		this.toggle_component(false);
		this.$component.find('.no-summary-placeholder').css('display', 'flex');
		this.$summary_wrapper.css('display', 'none');
	});

		this.$summary_container.on('click', '.email-btn', () => {
			this.email_dialog.fields_dict.email_id.set_value(this.customer_email);
		this.email_dialog.show();
	});

		this.$summary_container.on('click', '.print-btn', () => {
			this.print_receipt();
	});
	}

	print_receipt() {
		const frm = this.events.get_frm();
		frappe.utils.print(
			this.doc.doctype,
			this.doc.name,
			frm.pos_print_format,
			this.doc.letter_head,
			this.doc.language || frappe.boot.lang
		);
	}

	attach_shortcuts() {
		const ctrl_label = frappe.utils.is_mac() ? '⌘' : 'Ctrl';
		this.$summary_container.find('.print-btn').attr("title", `${ctrl_label}+P`);
		frappe.ui.keys.add_shortcut({
			shortcut: "ctrl+p",
			action: () => this.$summary_container.find('.print-btn').click(),
			condition: () => this.$component.is(':visible') && this.$summary_container.find('.print-btn').is(":visible"),
			description: __("Print Receipt"),
			page: cur_page.page.page
	});
		this.$summary_container.find('.new-btn').attr("title", `${ctrl_label}+Enter`);
		frappe.ui.keys.on("ctrl+enter", () => {
			const summary_is_visible = this.$component.is(":visible");
		if (summary_is_visible && this.$summary_container.find('.new-btn').is(":visible")) {
			this.$summary_container.find('.new-btn').click();
		}
	});
		this.$summary_container.find('.edit-btn').attr("title", `${ctrl_label}+E`);
		frappe.ui.keys.add_shortcut({
			shortcut: "ctrl+e",
			action: () => this.$summary_container.find('.edit-btn').click(),
			condition: () => this.$component.is(':visible') && this.$summary_container.find('.edit-btn').is(":visible"),
			description: __("Edit Receipt"),
			page: cur_page.page.page
	});
	}

	send_email() {
		const frm = this.events.get_frm();
		const recipients = this.email_dialog.get_values().email_id;
		const doc = this.doc || frm.doc;
		const print_format = frm.pos_print_format;

		frappe.call({
			method: "frappe.core.doctype.communication.email.make",
			args: {
				recipients: recipients,
				subject: __(frm.meta.name) + ': ' + doc.name,
				doctype: doc.doctype,
				name: doc.name,
				send_email: 1,
				print_format,
				sender_full_name: frappe.user.full_name(),
				_lang: doc.language
			},
			callback: r => {
			if (!r.exc) {
			frappe.utils.play_sound("email");
			if (r.message["emails_not_sent_to"]) {
				frappe.msgprint(__(
					"Email not sent to {0} (unsubscribed / disabled)",
					[ frappe.utils.escape_html(r.message["emails_not_sent_to"]) ]
				));
			} else {
				frappe.show_alert({
					message: __('Email sent successfully.'),
					indicator: 'green'
				});
			}
			this.email_dialog.hide();
		} else {
			frappe.msgprint(__("There were errors while sending email. Please try again."));
		}
	}
	});
	}

	add_summary_btns(map) {
		this.$summary_btns.html('');
		map.forEach(m => {
			if (m.condition) {
			m.visible_btns.forEach(b => {
				const class_name = b.split(' ')[0].toLowerCase();
			this.$summary_btns.append(
				`<div class="summary-btn btn btn-default ${class_name}-btn">${b}</div>`
			);
		});
		}
	});
		this.$summary_btns.children().last().removeClass('mr-4');
	}

	toggle_summary_placeholder(show) {
		if (show) {
			this.$summary_wrapper.css('display', 'none');
			this.$component.find('.no-summary-placeholder').css('display', 'flex');
		} else {
			this.$summary_wrapper.css('display', 'flex');
			this.$component.find('.no-summary-placeholder').css('display', 'none');
		}
	}

	get_condition_btn_map(after_submission) {
		if (after_submission)
			return [{ condition: true, visible_btns: ['New Order'] }];

		return [
			{ condition: this.doc.docstatus === 0, visible_btns: ['Edit Order', 'Delete Order'] },
			{ condition: !this.doc.is_return && this.doc.docstatus === 1, visible_btns: ['Print Receipt', 'Email Receipt', 'Return']},
			{ condition: this.doc.is_return && this.doc.docstatus === 1, visible_btns: ['Print Receipt', 'Email Receipt']}
		];
	}

	load_summary_of(doc, after_submission=false) {
		after_submission ?
			this.$component.css('grid-column', 'span 10 / span 10') :
			this.$component.css('grid-column', 'span 6 / span 6');

		this.toggle_summary_placeholder(false);

		this.doc = doc;

		this.attach_document_info(doc);

		this.attach_items_info(doc);

		this.attach_totals_info(doc);

		this.attach_payments_info(doc);

		const condition_btns_map = this.get_condition_btn_map(after_submission);

		this.add_summary_btns(condition_btns_map);
	}

	attach_document_info(doc) {
		frappe.db.get_value('Customer', this.doc.customer, 'email_id').then(({ message }) => {
			this.customer_email = message.email_id || '';
		const upper_section_dom = this.get_upper_section_html(doc);
		this.$upper_section.html(upper_section_dom);
	});
	}

	attach_items_info(doc) {
		this.$items_container.html('');
		doc.items.forEach(item => {
			const item_dom = this.get_item_html(doc, item);
		this.$items_container.append(item_dom);
		this.set_dynamic_rate_header_width();
	});
	}

	set_dynamic_rate_header_width() {
		const rate_cols = Array.from(this.$items_container.find(".item-rate-disc"));
		this.$items_container.find(".item-rate-disc").css("width", "");
		let max_width = rate_cols.reduce((max_width, elm) => {
			if ($(elm).width() > max_width)
		max_width = $(elm).width();
		return max_width;
	}, 0);

		max_width += 1;
		if (max_width == 1) max_width = "";

		this.$items_container.find(".item-rate-disc").css("width", max_width);
	}

	attach_payments_info(doc) {
		this.$payment_container.html('');
		doc.payments.forEach(p => {
			if (p.amount) {
			const payment_dom = this.get_payment_html(doc, p);
			this.$payment_container.append(payment_dom);
		}
	});
		if (doc.redeem_loyalty_points && doc.loyalty_amount) {
			const payment_dom = this.get_payment_html(doc, {
				mode_of_payment: 'Loyalty Points',
				amount: doc.loyalty_amount,
			});
			this.$payment_container.append(payment_dom);
		}
	}

	attach_totals_info(doc) {
		this.$totals_container.html('');

		const net_total_dom = this.get_net_total_html(doc);
		const taxes_dom = this.get_taxes_html(doc);
		const discount_dom = this.get_discount_html(doc);
		const grand_total_dom = this.get_grand_total_html(doc);
		this.$totals_container.append(net_total_dom);
		this.$totals_container.append(taxes_dom);
		this.$totals_container.append(discount_dom);
		this.$totals_container.append(grand_total_dom);
	}

	toggle_component(show) {
		show ? this.$component.css('display', 'flex') : this.$component.css('display', 'none');
	}
};