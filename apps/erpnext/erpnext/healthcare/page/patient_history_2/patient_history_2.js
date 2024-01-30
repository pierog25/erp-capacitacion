frappe.provide('frappe.patient_history_2');

// import Chart from 'chart.js/auto';
frappe.pages['patient-history-2'].on_page_load = async function(wrapper) {
	let me = this;

	var page = frappe.ui.make_app_page({

		parent: wrapper,
		title: 'Historia del paciente 2',
		single_column: true

	});
	frappe.breadcrumbs.add('Healthcare');

	let pid = '';

	page.main.html(frappe.render_template('patient_history_2', {}));

	page.main.find('.header-separator').hide();

	let patient = frappe.ui.form.make_control({
		parent: page.main.find('.patient'),
		df: {
			fieldtype: 'Link',
			options: 'Patient',
			fieldname: 'patient',
			placeholder: __('Select Patient'),
			only_select: true,
			change: async function() {
				let patient_id = patient.get_value();
				console.log(patient_id)
				if (pid != patient_id && patient_id) {
					me.start = 0;
					me.page.main.find('.patient_documents_list').html('');
					await setup_filters(patient_id, me);
					await get_documents(patient_id, me);
					// show_patient_info(patient_id, me);
					// show_patient_vital_charts(patient_id, me, 'bp', 'mmHg', 'Blood Pressure');
					pid = patient_id;
				}
			}
		},
	});

	patient.refresh();

}

const setup_filters = async (patient, me) => {
	$('.date-filter').empty();
	let date_range_field = frappe.ui.form.make_control({
		df: {
			fieldtype: 'DateRange',
			fieldname: 'date_range',
			placeholder: __('Date Range'),
			change: () => {
				let selected_date_range = date_range_field.get_value();
				console.log(selected_date_range)
				if (selected_date_range && selected_date_range.length === 2) {
					me.start = 0;
					me.page.main.find('.patient_documents_list').html('');
					get_documents(patient, me, selected_date_range);
				}
			}
		},
		parent: $('.date-filter')
	});
	date_range_field.refresh();
}

const get_documents = async (patient, me, selected_date_range = "") => {

	console.log( selected_date_range,'rango seleccionado' )
	const filters = [["paciente","=",patient]];

	if ( selected_date_range ){

		let fecha_uno = moment(selected_date_range[0]).format("YYYY-MM-DD")
		let fecha_dos = moment(selected_date_range[1]).format("YYYY-MM-DD")
		filters.push(['fecha_de_registro','between', [fecha_uno,fecha_dos]])
	}

	const registers = await frappe.db.get_list("Registro de Atenciones",{

		filters:filters,
		fields: ["name","paciente","fecha_de_registro","tipo_de_evento","sucursal","puesto","diagnostico_presuntivo","descripcion_de_malestrar"],
		limit: "None"

	})

	if ( registers.length ) {
		$('.date-filter').css('display', 'block')

		add_to_records(me, registers)

	} else {
		if(selected_date_range == ""){
			$('.date-filter').css('display', 'none')
		}

		let mensaje = `<div style="height: 200px; align-items: center; display: flex; justify-content: center;">
							<svg class="icon icon-sm" style="margin: 0 5px;"><use class="" href="#icon-restriction"></use></svg>
							<span>No se encontraron documentos para este paciente</span>
						</div>`
		me.page.main.find('.patient_documents_list').append(mensaje)

	}

}

const add_to_records = (me, data) => {

	let details = "<div class='widget-group-body grid-col-2 '>";
	let i;
	moment.locale("es");

	for (i=0; i<data.length; i++) {

		let theme_user = $("html").data("theme");
		const color_theme = theme_user == 'dark'?'1C2126':'fff';
		let fecha = data[i].fecha_de_registro  != ""? moment(data[i].fecha_de_registro).format("D MMMM YYYY").toString().toLocaleUpperCase() : ""
		let referenceDoctype = "Registro de Atenciones"
		let label = '';

		label += `<span class="link-item ellipsis" style="cursor: auto;">
					<span class="indicator-pill no-margin gray"></span>
					<span class="link-content ellipsis">Fecha de Registro ${data[i].fecha_de_registro}</span>
				</span>
				<span class="link-item ellipsis" style="cursor: auto;">
					<span class="indicator-pill no-margin gray"></span>
					<span class="link-content ellipsis">Puesto de Trabajo: ${data[i].puesto}</span>
				</span>
				<span class="link-item ellipsis" style="cursor: auto;">
					<span class="indicator-pill no-margin gray"></span>
					<span class="link-content ellipsis">Sucursal: ${data[i].sucursal}</span>
				</span>
				<span class="link-item ellipsis" style="cursor: auto;">
					<span class="indicator-pill no-margin gray"></span>
					<span class="link-content ellipsis">Tipo de Evento: ${data[i].tipo_de_evento}</span>
				</span>
				<span class="link-item ellipsis" style="cursor: auto;">
					<span class="indicator-pill no-margin gray"></span>
					<span class="link-content ellipsis">Diagnostico Presuntivo: ${data[i].diagnostico_presuntivo}</span>
				</span>`

		let time_line_heading = `<a class="link-item" onclick="frappe.set_route('Form', '${referenceDoctype}', '${data[i].name}');" target='_blank' style="margin: 0;"> ${data[i].name} </a>`;

		details += `
				<div class='widget links-widget-box'
					data-doctype='${referenceDoctype}' data-docname='${data[i].name}'>
					<div class="widget-head">
						<div class="widget-title ellipsis">${referenceDoctype} - ${time_line_heading} <span> - ${fecha} </span></div>
					</div>
					<div class='widget-body' >
						<span class='${referenceDoctype} document-id'>${label}</span>
						<span class='document-html' hidden  data-fetched="0"></span>
					</div>
				</div>`;

	}

	details += '</ul>';
	me.page.main.find('.patient_documents_list').append(details);

}