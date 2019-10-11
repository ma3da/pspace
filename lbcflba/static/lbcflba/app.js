Vue.component('modal', {
    template: '#modal-template',
    data: function () {
        return {
          text: '',
          block_id: null,
        };
    },
    methods: {
        close: function () {
            this.$emit('close');
            this.text = '';
        },
    }
})

Vue.component('daily', {
    methods: {
        getTimeStr(transaction) {
            return moment(transaction.time).format('DD MMM[,] H[h]mm')
        },
    },
    props: ["transaction"],
    template: `
    <table class="main_table">
        <tr>
            <td rowspan="2"> {{ transaction.amount }} </td>
            <td> {{ transaction.source }} -> {{ transaction.destination }} </td>
            <td colspan="2"> {{ getTimeStr(transaction) }} </td>
        </tr>
        <tr>
            <td> {{ transaction.text }} </td>
            <td> </td>
            <td @click="$emit('showmodify', transaction.id)"> {{ transaction.status }} </td>
        </tr>
        </table>
    `
})

new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        transactions: [],
        text: '',
        destination: 1,
        amount: 0,
        showNewModal: false,
        showModifyModal: false,
        fromto: 1,
        pk: null,
    },
    methods: {
        getAll: function () {
            axios
              .get('/lbcflba/api/all')
              .then(response => (this.transactions = response.data))
              .catch(error => printerr("getAll"));
        },
        newTransaction: function () {
            axios.post('/lbcflba/api/new',
                       {'destination': this.destination, 'text': this.text, 'amount': this.fromto * this.amount},
                       {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getAll()))
            .catch(error => this.printerr("status: " + error.response.status + "\n" + error.response.data))
            .then(() => {
                this.text = '';
                this.showNewModal = false;
            });
        },
        deleteTransaction: function () {
            axios.post('/lbcflba/api/delete', {'pk': this.pk}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getAll()))
            .catch(error => this.printerr("status: " + error.response.status + "\n" + error.response.data))
            .then(() => {
                this.pk = null;
                this.showModifyModal = false;
            });
        },
        test: function () {
            alert("testing testing");
        },
        printerr: function (err_msg) {
            alert("fail...\n" + err_msg);
        }
    },
    mounted() {
        this.getAll();
    }
})