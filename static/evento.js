// Anagrafica
function anagraficaForm() {
    return {
        formData: {
            nome_evento: "",
            stato: true,
            tipo_evento: "",
            responsabile: "",
            data_inizio: "",
            data_fine: "",
            localita: "",
            iscritti: "",
            quote_pagate: "",
            partecipanti: "",
            quota_acconto: "",
            quota_saldo: "",
            staff: "",
            quota_staff: "",
            iban: "",
        },
        elenco_tipi: [],
        elenco_account: [],
        eventoID: 1,
        formMessage: "",
            formLoading: false,
                async init() {
                    this.loadID();
                    await this.loadTipi();
                    await this.loadAccount();
                    await this.loadData();
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
                loadID() {
                    const parts = window.location.pathname.split("/").filter(Boolean);
                    this.eventoID = parts[parts.length - 1];
                },
                async loadData() {
                    try {
                        const response = await fetch(`/evento_data/${this.eventoID}`);
                        const data = await response.json();
                        this.formData.nome_evento = data.response.nome;
                        this.formData.stato = data.response.stato;
                        this.formData.tipo_evento = String(data.response.tipo);
                        this.formData.responsabile = String(data.response.responsabile);
                        this.formData.data_inizio = data.response.data_inizio;
                        this.formData.data_fine = data.response.data_fine;
                        this.formData.localita = data.response.localita;
                        this.formData.iscritti = data.response.iscritti;
                        this.formData.quote_pagate = data.response.quote_pagate;
                        this.formData.partecipanti = data.response.partecipanti;
                        this.formData.quota_acconto = data.response.quota_acconto;
                        this.formData.quota_saldo = data.response.quota_saldo;
                        this.formData.staff = data.response.staff;
                        this.formData.quota_staff = data.response.quota_staff;
                        this.formData.iban = data.response.iban;
                    } catch (err) {
                        console.error("Errore nel caricamento dati evento:", err);
                    }
                },
                submitForm() {
                    this.formMessage = "";
                    this.formLoading = true;
                    if (window.confirm("Stai aggiornando i dati dell'evento!")) {
                        fetch(`/evento_data/${this.eventoID}?tipo=update`, {
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
                toActive() {
                    this.formMessage = "";
                    this.formLoading = true;
                    if (window.confirm("Stai attivando l'evento.")) {
                        fetch(`/evento_data/${this.eventoID}?tipo=attiva`, {
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
                toDelete() {
                    this.formMessage = "";
                    this.formLoading = true;
                    if (window.confirm("Stai eliminando l'evento!")) {
                        fetch(`/evento_data/${this.eventoID}?tipo=elimina`, {
                            method: "DELETE",
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
                toSubmit() {
                    this.formMessage = "";
                    this.formLoading = true;
                    if (window.confirm("Stai sottomettendo l'evento.")) {
                        fetch(`/evento_data/${this.eventoID}?tipo=sottometti`, {
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


function evento_data_transazione() {
    return {
        elenco_transazioni: [],
        eventoID: 1,
        async init() {
            this.loadID();
            await this.refreshEventi();
        },
        loadID() {
            const parts = window.location.pathname.split("/").filter(Boolean);
            this.eventoID = parts[parts.length - 1];
        },
        async refreshEventi() {
            let response = await fetch(`/evento_data/${this.eventoID}?tipo=transazioni`);
            this.elenco_transazioni = await response.json();
        }
    }
}


function evento_data_rendiconto() {
    return {
        elenco_transazioni: [],
        eventoID: 1,
        async init() {
            this.loadID();
            await this.refreshEventi();
        },
        loadID() {
            const parts = window.location.pathname.split("/").filter(Boolean);
            this.eventoID = parts[parts.length - 1];
        },
        async refreshEventi() {
            let response = await fetch(`/evento_data/${this.eventoID}?tipo=rendiconto`);
            this.elenco_transazioni = await response.json();
        }
    }
}

function transazioneForm() {
    return {
        formData: {
            descrizione: "",
            tipo_transazione: 1,
            data: "",
            importo: 0,
        },
        elenco_tipi: [],
        formMessage: "",
        formLoading: false,
        eventoID: 1,
        async init() {
            this.loadID();
            await this.loadTipi();
        },
        loadID() {
            const parts = window.location.pathname.split("/").filter(Boolean);
            this.eventoID = parts[parts.length - 1];
        },
        async loadTipi() {
            let response = await fetch("/tipi_transazioni/manuali");
            this.elenco_tipi = await response.json();
            this.elenco_tipi = this.elenco_tipi.response;
        },
        loadData(id_tipo) {
            if (!id_tipo) {
                this.formData.descrizione = "";
                this.formData.tipo_transazione = "";
                this.formData.data = "";
                this.formData.importo = "";
            } else {
                fetch(`/transazioni/${id_tipo}`)
                .then(response => response.json())
                .then(data => {
                    this.formData.descrizione = data.response.id;
                    this.formData.nome = data.response.nome;
                });
            }
        },
        submitForm() {
            this.formMessage = "";
            this.formLoading = true;
            fetch(`/transazioni/${this.eventoID}`, {
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
    const eventoModal = document.getElementById('transazioneModal');

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
