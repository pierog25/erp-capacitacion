// Copyright (c) 2016, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
const diferenciaDeArreglos = (arr1, arr2) => {
	return arr1.filter(elemento => arr2.indexOf(elemento) == -1);
}

frappe.ui.form.on('Branch', {
	refresh: async function(frm) {
		const obtener_agencias_disponibles = await frappe.db.get_list('Branch', {
			filters: {
				'estado_de_sucursal': 1,
				'centro_de_costos_por_agencia': 0
			},
			fields: ['name'],
			limit: 'none'
		})
		const obtener_name_agencias_check_costo = await frappe.db.get_list('Branch', {
			filters: {
				'centro_de_costos_por_agencia': 1
			},
			fields: ['name'],
			limit: 'none'
		})
		if ( obtener_name_agencias_check_costo.length === 0 ) {
			let arrayAgenciaDisponible = obtener_agencias_disponibles.map(agencyYes => agencyYes.name);
			frm.fields_dict.costo_por_agencia_tabla.grid.update_docfield_property('agencia','options',[''].concat(arrayAgenciaDisponible.sort()))
			return false
		}
		let arrayAgenciaCheckCosto = []
		for ( let agency of obtener_name_agencias_check_costo ) {
			arrayAgenciaCheckCosto.push(agency.name)
		}
		const obtener_agencias_no_disponible = await frappe.db.get_list('Tabla Costo por Agencia',{
			'filters':[
				['parent','in',arrayAgenciaCheckCosto],
			],
			'limit':'None',
			'fields': ['agencia']
		});
		let arrayAgenciaNoDisponible = obtener_agencias_no_disponible.map(agencyNot => agencyNot.agencia)
			.filter((value, index, self) => self.indexOf(value) === index);
		let arrayAgenciaDisponible = obtener_agencias_disponibles.map(agencyYes => agencyYes.name);
		let difference2 = arrayAgenciaDisponible.filter(x => !arrayAgenciaNoDisponible.includes(x));
		frm.fields_dict.costo_por_agencia_tabla.grid.update_docfield_property('agencia','options',[''].concat(difference2.sort()))
	},
	centro_de_costos_por_agencia: async function(frm) {

		if ( frm.doc.centro_de_costos_por_agencia === 0 ) {
			frm.set_value('costo_por_agencia_tabla',[])
		}

		const obtener_agencias_no_disponible = await frappe.db.get_list('Tabla Costo por Agencia',{
			'limit':'None',
			'fields': ['agencia','name','parent']
		});

		let valueCheck = false

		for ( let item of obtener_agencias_no_disponible ) {
			if ( item.agencia === frm.doc.name ) {
				frappe.msgprint("Esta agencia ya se encuentra dentro de " + item.parent )
				frm.set_value('centro_de_costos_por_agencia',0)
				valueCheck = true
			}
		}

		if ( !valueCheck ) {
			frm.save()
		}
	}
});

frappe.ui.form.on('Tabla Costo por Agencia', {
	async agencia(frm, cdt, cdn) {
		let item = locals[cdt][cdn];

		console.log(item)
		console.log(cur_frm.get_field("costo_por_agencia_tabla").grid.grid_rows)
		if ( item.agencia && item.agencia === frm.doc.name ) {
			cur_frm.get_field("costo_por_agencia_tabla").grid.grid_rows[parseInt(item.idx) - 1].remove();
			frappe.throw("No puede agregar la misma sucursal")
			return false
		}

		let get_id_agency = await frappe.db.get_value('Branch', item.agencia, 'ideentificador')
		let id_branch = get_id_agency.message.ideentificador
		item.id = id_branch
		if (frm.doc.costo_por_agencia_tabla.length > 1) {
			var tbl = frm.doc.costo_por_agencia_tabla || [];
			var countMap = {};

			// Contar la cantidad de veces que aparece cada agencia
			tbl.forEach(function(item) {
				if (countMap[item.agencia]) {
					countMap[item.agencia]++;
				} else {
					countMap[item.agencia] = 1;
				}
			});

			// Eliminar las filas si el nombre de la agencia se repite más de dos veces
			tbl.forEach(function(item, index) {
				if (countMap[item.agencia] > 1) {
					cur_frm.get_field("costo_por_agencia_tabla").grid.grid_rows[index].remove();
					frappe.throw('Las sucursales duplicadas han sido eliminadas');
				}
			});
		}
	}
});
