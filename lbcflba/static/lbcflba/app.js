Vue.component('modal', {
    template: '#modal-template',
    data: function () {
        return {
          text: '',
          pk: null,
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
        getAmountStyle(transaction) {
            color = "Gray";
            return {color: color, background: "white", width: "10%"};
        },
    },
    props: ["transaction"],
    template: `
    <table class="main_table" style="border: 2px solid #eeeeee; color: Gray; background: #eeeeee">
        <tr>
            <td rowspan="2" v-bind:style="getAmountStyle(transaction)"> {{ transaction.amount }} </td>
            <td style="text-align: left"> >> </td>
            <td colspan="2" style="text-align: right"> {{ getTimeStr(transaction) }} </td>
        </tr>
        <tr>
            <td style="width: 80%"> {{ transaction.text }} </td>
            <td> </td>
            <td style="width: 10%" @click="$emit('showmodify', transaction.id)"> {{ transaction.status }} </td>
        </tr>
    </table>
    `
})

Vue.component('recap', {
    data: function () {
        return {
          sum: 0
        }
    },
    methods: {
        computeSum(transactions) {
            sum = 0;
            for (transaction of transactions) {
                sum += parseFloat(transaction.amount)
            }
            this.sum = sum
            return sum.toFixed(2)
        },
        getSumStyle(sum) {
            if (sum > 0) {
                color =  "MediumSeaGreen";
            } else if (sum < 0) {
                color = "Tomato";
            } else {
                color = "Gray";
            }
            return {color: color};
        },
    },
    props: ["transactions"],
    template: `
    <table class="main_table" style="border: 1px solid #eeeeee">
        <tr>
            <td v-bind:style="getSumStyle(sum)"> {{ computeSum(transactions) }}</td>
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
        other: 1,
        amount: 0,
        showNewModal: false,
        showModifyModal: false,
        direction: 1,
        pk: null,
        groups: [],
        members: [],
        selectedGroupId: null,
        selectedGroupTransactions: [],
    },
    methods: {
        getAll: function () {
            axios
              .get('/lbcflba/api/all')
              .then(response => (this.transactions = response.data))
              .catch(error => printerr("getAll::transactions"));
            this.getGroups();
        },
        groupGotSelected: function () {
            this.getMembers(this.selectedGroupId);
            transactions = [];
            for (transaction of this.transactions) {
                if (transaction.destination == this.selectedGroupId) {
                    transactions.push(transaction);
                }
            }
            this.selectedGroupTransactions = transactions;
        },
        getGroups: function() {
            axios
              .get('/lbcflba/api/groups')
              .then(response => (this.groups = response.data))
              .catch(error => printerr("status: " + error.response.status + "\n" + error.response.data));
        },
        getMembers: function(groupId) {
            if (groupId == null) {
                return [];
            }
            axios
              .get('/lbcflba/api/members/' + groupId)
              .then(response => (this.members = response.data))
              .catch(error => printerr("status: " + error.response.status + "\n" + error.response.data));
        },
        newTransaction: function () {
            axios.post('/lbcflba/api/new',
                       {'destination': this.selectedGroupId, 'text': this.text, 'amount': this.amount},
                       {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getAll()))
            .catch(error => this.printerr("status: " + error.response.status + "\n" + error.response.data))
            .then(() => {
                this.text = '';
                this.showNewModal = false;
                this.groupGotSelected();
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
        },
    },
    mounted() {
        this.getAll();
    }
})
