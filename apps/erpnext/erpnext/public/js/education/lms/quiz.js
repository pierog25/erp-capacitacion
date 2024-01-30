class Quiz {
	constructor(wrapper, options) {
		this.wrapper = wrapper;
		Object.assign(this, options);
		this.questions = []
		this.refresh();
	}

	refresh() {
		this.get_quiz();
	}

	get_quiz() {
		frappe.call('erpnext.education.utils.get_quiz', {
			quiz_name: this.name,
			course: this.course
		}).then(res => {
			this.make(res.message)
		});
	}

	make(data) {
		if (data.is_time_bound) {
			$(".lms-timer").removeClass("hide");
			if (!data.activity || (data.activity && !data.activity.is_complete)) {
				this.initialiseTimer(data.duration);
				this.is_time_bound = true;
				this.time_taken = 0;
			}
		}
		data.questions.forEach(question_data => {
			let question_wrapper = document.createElement('div');
		let question = new Question({
			wrapper: question_wrapper,
			...question_data
		});
		this.questions.push(question)
		this.wrapper.appendChild(question_wrapper);
	})
		if (data.activity && data.activity.is_complete) {
			this.disable()
			let indicator = 'red'
			let message = 'No se le permite volver a intentar la prueba.'
			if (data.activity.result == 'Pass') {
				indicator = 'green'
				message = 'Ya ha completado el cuestionario.'
			}
			if (data.activity.time_taken) {
				this.calculate_and_display_time(data.activity.time_taken, "Tiempo tomado - ");
			}
			this.set_quiz_footer(message, indicator, data.activity.score)
		}
		else {
			this.make_actions();
		}
		window.addEventListener('beforeunload', (event) => {
			event.preventDefault();
		event.returnValue = '';
	});
	}

	initialiseTimer(duration) {
		this.time_left = duration;
		var self = this;
		var old_diff;
		this.calculate_and_display_time(this.time_left, "Tiempo restante - ");
		this.start_time = new Date().getTime();
		this.timer = setInterval(function () {
			var diff = (new Date().getTime() - self.start_time)/1000;
			var variation = old_diff ? diff - old_diff : diff;
			old_diff = diff;
			self.time_left -= variation;
			self.time_taken += variation;
			self.calculate_and_display_time(self.time_left, "Tiempo restante - ");
			if (self.time_left <= 0) {
				clearInterval(self.timer);
				self.time_taken -= 1;
				self.submit();
			}
		}, 1000);
	}

	calculate_and_display_time(second, text) {
		var timer_display = document.getElementsByClassName("lms-timer")[0];
		var hours = this.append_zero(Math.floor(second / 3600));
		var minutes = this.append_zero(Math.floor(second % 3600 / 60));
		var seconds = this.append_zero(Math.ceil(second % 3600 % 60));
		timer_display.innerText = text + hours + ":" + minutes + ":" + seconds;
	}

	append_zero(time) {
		return time > 9 ? time : "0" + time;
	}

	make_actions() {
		const button = document.createElement("button");
		button.classList.add("btn", "btn-primary", "mt-5", "mr-2");

		button.id = 'submit-button';
		button.innerText = 'Submit';
		button.onclick = () => this.submit();
		this.submit_btn = button
		this.wrapper.appendChild(button);
	}

	submit() {
		if (this.is_time_bound) {
			clearInterval(this.timer);
			$(".lms-timer").text("");
		}
		this.submit_btn.innerText = 'Evaluating..'
		this.submit_btn.disabled = true
		this.disable()
		frappe.call('erpnext.education.utils.evaluate_quiz', {
			quiz_name: this.name,
			quiz_response: this.get_selected(),
			course: this.course,
			program: this.program,
			time_taken: this.is_time_bound ? this.time_taken : 0
		}).then(res => {
			$(".form-check-input").each((index,item)=>{
			let inp = $(item)[0]
			if(inp.checked){
			let parent = inp.parentElement
			let htmlTest = "";
			if(res.message.result[inp.name]){
				parent.childNodes[1].style.color = "green";
				htmlTest = parent.innerHTML;
				htmlTest+= ` 
							<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor" class="bi bi-check" viewBox="0 0 16 16" style="color: green;">
						  		<path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"></path>
							</svg>
						`
			}else{
				parent.childNodes[1].style.color = "red";
				htmlTest = parent.innerHTML;
				htmlTest+= ` 
							<svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" fill="currentColor" class="bi bi-x" viewBox="0 0 16 16" style="color: red;">
							  <path d="M4.646 4.646a.5.5 0 0 1 .708 0L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 0 1 0-.708z"/>
							</svg>
						`
			}
			parent.innerHTML = htmlTest
		}
	})
		this.submit_btn.remove()
		if (!res.message) {
			frappe.throw(__("Algo salió mal al evaluar el cuestionario"))
		}

		let indicator = 'red'
		let attemps = res.message.quiz.max_attempts
		let attemps_made = res.message.quizes
		let message2 = ""
		if (attemps == attemps_made) {
			message2 = "Te quedaste sin intentos"
		} else {
			if((attemps - attemps_made) == 1){
				message2 = `Te quedan ${attemps - attemps_made} intento para realizar el examen`
			}else{
				message2 = `Te quedan ${attemps - attemps_made} intentos para realizar el examen`
			}
		}
		let message = 'Desaprobaste. '+message2
		if (res.message.status == 'Pass') {
			indicator = 'green'
			message = 'Felicitaciones, aprobaste el examen.'
		}
		frappe.msgprint({
			title: res.message.quiz.name,
			indicator: indicator,
			message: message
		});
		this.set_quiz_footer(message, indicator, res.message.score)
	});
	}

	set_quiz_footer(message, indicator, score) {
		const div = document.createElement("div");
		div.classList.add("mt-5");
		div.innerHTML = `<div class="row">
							<div class="col-md-8">
								<h4>${message}</h4>
								<h5 class="text-muted"><span class="indicator ${indicator}">Puntaje: ${score}/100</span></h5>
							</div>
							<div class="col-md-4">
								<a href="${this.next_url}" class="btn btn-primary pull-right">${this.quiz_exit_button}</a>
							</div>
						</div>`

		this.wrapper.appendChild(div)
	}

	disable() {
		this.questions.forEach(que => que.disable())
	}

	get_selected() {
		let que = {}
		this.questions.forEach(question => {
			que[question.name] = question.get_selected()
		})
		return que
	}
}

class Question {
	constructor(opts) {
		Object.assign(this, opts);
		this.make();
	}

	make() {
		this.make_question()
		this.make_options()
	}

	get_selected() {
		let selected = this.options.filter(opt => opt.input.checked)
		if (this.type == 'Single Correct Answer') {
			if (selected[0]) return selected[0].name
		}
		if (this.type == 'Multiple Correct Answer') {
			return selected.map(opt => opt.name)
		}
		return null
	}

	disable() {
		let selected = this.options.forEach(opt => opt.input.disabled = true)
	}

	make_question() {
		let question_wrapper = document.createElement('h5');
		question_wrapper.classList.add('mt-3');
		question_wrapper.innerHTML = this.question;
		this.wrapper.appendChild(question_wrapper);
	}

	make_options() {
		let make_input = (name, value) => {
			let input = document.createElement('input');
			input.id = name;
			input.name = this.name;
			input.value = value;
			input.type = 'radio';
			if (this.type == 'Multiple Correct Answer')
				input.type = 'checkbox';
			input.classList.add('form-check-input');
			return input;
		}

		let make_label = function (name, value) {
			let label = document.createElement('label');
			label.classList.add('form-check-label');
			label.htmlFor = name;
			label.innerText = value;
			return label
		}

		let make_option = function (wrapper, option) {
			let option_div = document.createElement('div');
			option_div.classList.add('form-check', 'pb-1');
			let input = make_input(option.name, option.option);
			let label = make_label(option.name, option.option);
			option_div.appendChild(input);
			option_div.appendChild(label);
			wrapper.appendChild(option_div);
			return { input: input, ...option };
		}

		let options_wrapper = document.createElement('div')
		options_wrapper.classList.add('ml-2')
		let option_list = []
		this.options.forEach(opt => option_list.push(make_option(options_wrapper, opt)))
		this.options = option_list
		this.wrapper.appendChild(options_wrapper)
	}
}
