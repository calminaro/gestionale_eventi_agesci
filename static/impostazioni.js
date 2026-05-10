// System Option

function system_optionForm() {
    return {
        formData: {
            id_ente: "",
            nome_iro: "",
            cognome_iro: "",
            smtp_server: "",
            smtp_port: "",
            mail_indirizzo: "",
            mail_passwd: "",
        },
        formMessage: "",
            formLoading: false,
                loadData() {
                    fetch(`/system_option`)
                    .then(response => response.json())
                    .then(data => {
                        this.formData.id_ente = data.response.id_ente;
                        this.formData.nome_iro = data.response.nome_iro;
                        this.formData.cognome_iro = data.response.cognome_iro;
                        this.formData.smtp_server = data.response.smtp_server;
                        this.formData.smtp_port = data.response.smtp_port;
                        this.formData.mail_indirizzo = data.response.mail_indirizzo;
                        this.formData.mail_passwd = data.response.mail_passwd;
                    });
                },
                submitForm() {
                    this.formMessage = "";
                    this.formLoading = true;
                    if (window.confirm("Stai aggiornando le System Option.")) {
                        fetch("/system_option", {
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
                    };
                    this.formLoading = false;
                },
    };
}


// Tipi Eventi
function tipi_eventi() {
    return {
        elenco_eventi: '',
        async init() {
            await this.refreshEventi();
        },
        async refreshEventi() {
            let response = await fetch("/tipi_eventi");
            this.elenco_eventi = await response.json();
        }
    }
}

function tipiEventiForm() {
    return {
        formData: {
            tipo_id: "",
            nome: "",
        },
        formMessage: "",
        formLoading: false,
            init() {
                this.loadData();
            },
            loadData(id_tipo) {
                if (!id_tipo) {
                    this.formData.tipo_id = "";
                    this.formData.nome = "";
                } else {
                    fetch(`/tipi_eventi/${id_tipo}`)
                    .then(response => response.json())
                    .then(data => {
                        this.formData.tipo_id = data.response.id;
                        this.formData.nome = data.response.nome;
                    });
                }
            },
            submitForm() {
                this.formMessage = "";
                this.formLoading = true;
                fetch("/tipi_eventi", {
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
    const tipiModal = document.getElementById('tipiModal');

    if (tipiModal) {
        tipiModal.addEventListener('show.bs.modal', event => {
            const button = event.relatedTarget;
            const id_tipo = button.getAttribute('data-bs-tipoid');

            const modalComponent = Alpine.$data(tipiModal.querySelector('[x-data]'));

            if (modalComponent) {
                modalComponent.loadData(id_tipo);
            }
        });
    }
});
