function sidebarData() {
    return {
        data: '',
        id_ente: localStorage.getItem("id_ente"),
        username: localStorage.getItem("username"),
        async init() {
            let response = await fetch("/sidebardata");
            this.data = await response.json();
            localStorage.setItem("id_ente", this.data.response.id_ente);
            localStorage.setItem("username", this.data.response.username);
        }
    }
}
