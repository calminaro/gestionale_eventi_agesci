function data_oggi() {
    const today = new Date();
    let day = today.getDate();
    let month = today.getMonth() + 1;
    const year = today.getFullYear();
    if (day < 10) {
        day = '0' + day;
    }
    if (month < 10) {
        month = '0' + month;
    }
    const formattedDate = `${year}-${month}-${day}`;
    return formattedDate
}

function eventi() {
    return {
        elenco_eventi: false,
        async init() {
            await this.refreshEventi();
        },
        async refreshEventi() {
            let response = await fetch("/eventi_list");
            this.elenco_eventi = await response.json();
        }
    }
}

function eventiForm() {
    return {
        formData: {
            nome: "",
            tipo_evento: 1,
            account_responsabile: 1,
        },
        elenco_tipi: [],
        elenco_account: [],
        formMessage: "",
            formLoading: false,
                async init() {
                    await this.loadTipi();
                    await this.loadAccount();
                },
                async loadTipi() {
                    let response = await fetch("/tipi_eventi");
                    this.elenco_tipi = await response.json();
                    this.elenco_tipi = this.elenco_tipi.response;
                },
                async loadAccount() {
                    let response = await fetch("/user");
                    this.elenco_account = (await response.json()).response;
                },
                submitForm() {
                    this.formMessage = "";
                    this.formLoading = true;
                    fetch("/eventi_list", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            Accept: "application/json",
                        },
                        body: JSON.stringify(this.formData),
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Network response was not ok');
                        }
                        return response.json();
                    })
                    .then((data) => {
                        if (data.response == "ok") {
                            document.getElementById("refresh_eventi").click();
                        }
                    })
                    .finally(() => {
                        this.formLoading = false;
                    });
                },
    };
}

document.addEventListener('DOMContentLoaded', function () {
    const eventoModal = document.getElementById('eventoModal');

    if (eventoModal) {
        eventoModal.addEventListener('show.bs.modal', event => {
            const button = event.relatedTarget;
            const evento_id = button.getAttribute('data-bs-eventoid');

            const modalComponent = Alpine.$data(eventoModal.querySelector('[x-data]'));

            if (modalComponent) {
                modalComponent.loadData(evento_id);
            }
        });
    }
});
