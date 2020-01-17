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
            return moment(transaction.date).format('DD MMM')
        },
        getAmountStyle(transaction, spenderId) {
            var color = transaction.source == spenderId ? "Tomato" : "CornFlowerBlue";
            return {color: color, background: "white", width: "10%", "font-size": "1.2em"};
        },
        getStatusColor(status) {
            return "Gray";
        },
    },
    props: ["transaction", "userinfo", "memberdict", "categorydict"],
    template: `
    <table class="transaction_table" :style="{border: '2px solid ' + getStatusColor(transaction.status), color: 'Gray'}" @click="$emit('showupdate', transaction.id)">
        <tr>
            <td rowspan="3" v-bind:style="getAmountStyle(transaction, userinfo.spenderId)"> {{ transaction.amount }} </td>
            <td rowspan="2" colspan="2" style="min-width: 80%"> {{ transaction.text }} </td>
            <td rowspan="3" :style="{width: '5%', background: getStatusColor(transaction.status), color: '#eeeeee'}"> {{ transaction.status }} </td>
        </tr>
        <tr></tr>
        <tr>
            <td :style="{'font-size': '0.8em', 'vertical-align': 'bottom', 'padding-bottom':'0'}"> {{ memberdict[transaction.source].username }}, {{ getTimeStr(transaction) }}, {{ categorydict[transaction.category] }} </td>
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
        computeShares(transactions, memberdict) {
            var shares = {};
            for (id in memberdict) {
                shares[id] = 0
            }
            var total = 0;
            for (t of transactions) {
                shares[t.source] += parseFloat(t.amount);
                total += parseFloat(t.amount);
            }
            var mean = total / Object.keys(memberdict).length;
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
                symbol =  "<i class='fa fa-long-arrow-left'></i>";
            } else if (amount < 0) {
                symbol =  "<i class='fa fa-long-arrow-right'></i>";
            } else {
                symbol = "==";
            }
            return symbol;
        }
    },
    props: ["transactions", "userinfo", "memberdict"],
    template: `
    <table class="recap_table" style="border: 1px solid #eeeeee">
        <tr v-for="(amount, id) in computeShares(transactions, memberdict)">
            <td> {{ memberdict[id].username }} </td>
            <td> <span v-html="getArrow(parseFloat(amount))"></span> </td>
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
        groups: [],

        selectedGroupId: -1,

        filterData: {
            statusId: -1,
            categoryId: -1,
        },

        userData: {
            name: "",
        },

        newData: {
            sourceId: null,
            text: '',
            amount: null,
            categoryId: 0,
            fastState: 0,
        },

        updateData: {
            pk: null,
            text: '',
            categoryId: 0,
            date: null,
        },

        optionData: {
            categoryName: '',
            categoryId: 0,
        },

        showNewModal: false,
        showFastNewModal: false,
        showUpdateModal: false,
        showOptionModal: false,
        showFilterModal: false,
        showChooseModal: false,
    },
    computed: {
        groupDict: function() {
            var d = {};
            for (group of this.groups) {
                d[group.id] = group;
            }
            return d;
        },
        categoryDict: function() {
            var sid = this.selectedGroupId;
            console.log(sid)
            console.log(this.groups)
            console.log(this.groupDict)
                if (sid > -1){
                    return this.groupDict[sid].categoryDict;
                }
                return {};
        },
        members: function() {
            sid = this.selectedGroupId
            if (sid > -1);
                return this.groupDict[sid].members;
            return [];
        },
        memberDict: function() {
            var d = {};
            for (member of this.members) {
                d[member.spenderId.toString()] = member;
            }
            return d;
        },
        selectedGroupTransactions: function() {
            var sid = this.selectedGroupId;
            if (sid > -1)
                return this.transactions
                  .filter(t => (t.destination == sid))
                  .filter(this.isSelected);
            return [];
        },
        transactionDict: function() {
            var d = {};
            for (transaction of this.transactions) {
                d[transaction.id] = transaction;
            }
            return d;
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
                this.clearNewData();
                this.showNewModal = false;      // wrong place
                this.showFastNewModal = false;  //
            });
        },
        deleteTransaction: function () {
            axios.post(
                '/lbcflba/api/delete',
                {'pk': this.updateData.pk},
                {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getTransactions()))
            .catch(this.printResponseError)
            .then(() => {
                this.clearUpdateData();
                this.showUpdateModal = false;   // wrong place
            });
        },
        updateTransaction: function () {
            axios.post(
                '/lbcflba/api/update',
                {
                    'pk': this.updateData.pk,
                    'text': this.updateData.text,
                    'categoryId': this.updateData.categoryId,
                    'date': this.updateData.date
                },
                {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getTransactions()))
            .catch(this.printResponseError)
            .then(() => {
                this.clearUpdateData();
                this.showUpdateModal = false;
            });
        },
        newCategory: function () {
            axios.post(
                '/lbcflba/api/group/category/new',
                {'groupId': this.selectedGroupId, 'categoryName': this.optionData.categoryName},
                {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => this.getGroups())
            .catch(this.printResponseError)
            .then(() => {
                this.optionData.categoryName = '';
            });
        },
        deleteCategory: function (groupId, categoryId) {
            axios.post(
                '/lbcflba/api/group/category/delete',
                {'groupId': this.selectedGroupId, 'categoryId': this.optionData.categoryId},
                {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => this.getGroups())
            .catch(this.printResponseError)
            .then(() => {
                this.optionData.categoryId = 0;
            });
        },
        renameGroup: function() {
            axios.post('/lbcflba/api/group/update',
                {'groupId': this.selectedGroupId, 'name': this.optionData.groupName},
                {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => this.getGroups())
            .catch(this.printResponseError)
            .then(() => {
                this.optionData.groupName = "";
            });
        },
        renameUser: function() {
            axios.post('/lbcflba/api/userinfo',
                {'username': this.userData.name},
                {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => this.getUserInfo())
            .catch(this.printResponseError)
            .then(() => {
                this.userData.name = "";
                this.getUserInfo();
                this.getGroups();
            });
            
        },

        processFastState: function(actualState, data) {
            if (actualState == 0) {
                spenderId = data;
                this.newData.sourceId = spenderId;
                this.newData.fastState += 1; // skip next, for now
            }
            else if (actualState == 1) {
//                spenderId = data;
//                this.newData.destination = spenderId;
            }
            else if (actualState == 2) {
            }
            else if (actualState == 3) {
                this.newTransaction();
                return;
            }

            this.newData.fastState += 1;
        },
        closeFastNewModal: function() {
            this.showFastNewModal = false;
            this.clearNewData();
        },

        isSelected: function(transaction) {
            var boolStatus = this.filterData.statusId < 0 || (this.filterData.statusId == transaction.status);
            var boolCategory = this.filterData.categoryId < 0 || (this.filterData.categoryId == transaction.category);
            return boolStatus && boolCategory;
        },
        clearFilters: function() {
            this.filterData = {
                statusId: -1,
                categoryId: -1,
            };
        },
        clearNewData: function() {
            this.newData.sourceId = null;
            this.newData.text = '';
            this.newData.amount = 0;
            this.newData.categoryId = 0;
            this.newData.fastState = 0;
        },
        setUpdateDataTo: function(transaction) {
            this.updateData.pk = transaction.id;
            this.updateData.text = transaction.text;
            this.updateData.categoryId = transaction.category;
            this.updateData.date = transaction.date;
        },
        clearUpdateData: function() {
            this.updateData.pk = null;
            this.updateData.text = "";
            this.updateData.categoryId = 0;
            this.updateData.date = null;
        },
        doShowUpdateModal: function(transationId) {
            this.setUpdateDataTo(this.transactionDict[transationId]);
            this.showUpdateModal = true;
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
        this.groupDict;
    }
})
