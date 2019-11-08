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
        getMemberName: function(mId, members) {
            for (member of members) {
                if (member.spenderId == mId) {
                    return member.username;
                }
            }
            return "???"
        },
        getTimeStr(transaction) {
            return moment(transaction.time).format('DD MMM[.] H[h]mm')
        },
        getAmountStyle(transaction, spenderId) {
            if (transaction.source == spenderId) {
                color = "Tomato";
            } else {
                color =  "CornFlowerBlue";
            }
            return {color: color, background: "white", width: "10%", "font-size": "1.2em"};
        },
        getStatusColor(status) {
            return "Gray";
        },
    },
    props: ["transaction", "userinfo", "members", "categorydict"],
    template: `
    <table class="transaction_table" :style="{border: '2px solid ' + getStatusColor(transaction.status), color: 'Gray'}">
        <tr>
            <td rowspan="3" v-bind:style="getAmountStyle(transaction, userinfo.spenderId)"> {{ transaction.amount }} </td>
            <td rowspan="2" colspan="2" style="min-width: 80%"> {{ transaction.text }} </td>
            <td rowspan="3" :style="{width: '5%', background: getStatusColor(transaction.status), color: '#eeeeee'}" @click="$emit('showmodify', transaction.id)"> {{ transaction.status }} </td>
        </tr>
        <tr></tr>
        <tr>
            <td :style="{'font-size': '0.8em', 'vertical-align': 'bottom', 'padding-bottom':'0'}"> {{ getMemberName(transaction.source, members) }}, {{ getTimeStr(transaction) }}, {{ categorydict[transaction.category] }} </td>
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
        getMemberName: function(mId, members) {
            for (member of members) {
                if (member.spenderId == mId) {
                    return member.username;
                }
            }
            return "???"
        },
        computeShares(transactions, members) {
            shares = {};
            for (member of members) {
                shares[member.spenderId] = 0
            }
            total = 0;
            for (t of transactions) {
                shares[t.source] += parseFloat(t.amount);
                total += parseFloat(t.amount);
            }
            mean = total / members.length;
            for (id in shares) {
                shares[id] -= mean;
                shares[id] = shares[id].toFixed(2);
            }
            return shares;
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
        getArrow(amount) {
            if (amount > 0) {
                symbol =  "<=";
            } else if (amount < 0) {
                symbol =  "=>";
            } else {
                symbol = "==";
            }
            return symbol;
        }
    },
    props: ["transactions", "userinfo", "members"],
    template: `
    <table class="recap_table" style="border: 1px solid #eeeeee">
        <tr v-for="(amount, id) in computeShares(transactions, members)">
            <td> {{ getMemberName(id, members) }} </td>
            <td> {{ getArrow(parseFloat(amount)) }} </td>
            <td :style="getSumStyle(amount)"> {{ amount }} </td>
        </tr>
    </table>
    `
})

new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        userInfo: {},
        transactions: [],
        pk: null,
        groups: [],
        selectedGroupId: -1,

        status: -1,
        categoryId: -1,

        newData: {
            sourceId: null,
            text: '',
            amount: 0,
            categoryId: 0,
        },

        showNewModal: false,
        showModifyModal: false,
        showOptions: false,
    },
    computed: {
        categoryDict: function() {
            sid = this.selectedGroupId;
                if (sid > -1)
                    return this.groupDict[this.selectedGroupId].categoryDict;
                return {};
        },
        groupDict: function() {
            d = {};
            for (group of this.groups) {
                d[group.id.toString()] = group;
            }
            return d;
        },
        selectedGroupTransactions: function() {
            sid = this.selectedGroupId;
            if (sid > -1)
                return this.transactions
                  .filter(t => (t.destination == sid))
                  .filter(this.isSelected);
            return [];
        },
        members: function() {
            sid = this.selectedGroupId
            if (sid > -1);
                return this.groupDict[sid].members;
            return [];
        },
    },
    methods: {
        getTransactions: function () {
            axios
              .get('/lbcflba/api/all')
              .then(response => {this.transactions = response.data;})
              .catch(this.printResponseError);
        },
        getGroups: function() {
            axios
              .get('/lbcflba/api/groups')
              .then(response => {this.groups = response.data;})
              .catch(this.printResponseError);
        },
        getUserInfo: function() {
            axios
              .get('/lbcflba/api/userinfo')
              .then(response => {this.userInfo = response.data; this.newData.sourceId = this.userInfo.spenderId;})
              .catch(this.printResponseError);
        },

        newTransaction: function () {
            axios.post('/lbcflba/api/new',
                {
                   'destination': this.selectedGroupId, 'source': this.newData.sourceId,
                   'text': this.newData.text,
                   'amount': this.newData.amount,
                   'category': this.newData.categoryId
                },
                {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => this.getTransactions())
            .catch(this.printResponseError)
            .then(() => {
                this.newData.text = '';
                this.newData.amount = 0;
                this.showNewModal = false;
            });
        },
        deleteTransaction: function () {
            axios.post('/lbcflba/api/delete', {'pk': this.pk}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getTransactions()))
            .catch(this.printResponseError)
            .then(() => {
                this.pk = null;
                this.showModifyModal = false;
            });
        },
        newCategory: function (groupId, categoryName) {
            axios.post('/lbcflba/api/group/category/new', {'groupId': groupId, 'categoryName': categoryName}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => this.getGroups())
            .catch(this.printResponseError);
        },
        deleteCategory: function (groupId, categoryId) {
            axios.post('/lbcflba/api/group/category/delete', {'groupId': groupId, 'categoryId': categoryId}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => this.getGroups())
            .catch(this.printResponseError);
        },

        isSelected: function(transaction) {
            boolStatus = this.status < 0 || (this.status == transaction.status);
            boolCategory = this.categoryId < 0 || (this.categoryId == transaction.category);
            return boolStatus && boolCategory;
        },

        printerr: function (err_msg) {
            alert("prout\n\n" + err_msg);
        },
        printResponseError: function (error) {
            this.printerr("status: " + error.response.status + "\n\n" + JSON.stringify(error.response.data));
        },
    },
    mounted() {
        this.getUserInfo();
        this.getTransactions();
        this.getGroups();
    }
})
