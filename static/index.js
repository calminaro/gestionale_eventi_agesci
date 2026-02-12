function LoginForm() {
    return {
        formData: {
            username: "",
            passwd: "",
        },
        formMessage: "",
        formLoading: false,
        loginButtonText: "Accedi",
        submitForm() {
            this.formMessage = "";
            this.formLoading = true;
            fetch("/login", {
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
                this.formData.username = "";
                this.formData.passwd = "";
                if (data.response == "no_user") {
                    window.location.href = "/welcome";
                    this.formMessage = "Qualcosa non va";
                } else if (data.response == "success") {
                    window.location.href = "/dashboard";
                } else if (data.response == "invalid") {
                    this.formMessage = "Username o password errati";
                }
            })
            .finally(() => {
                this.formLoading = false;
            });
        },
    };
}
