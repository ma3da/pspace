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
        getTimeStartStr(block) {
            return moment(block.time_start).format('H[h]mm')
        },
        getTimeStopStr(block) {
            return moment(block.time_end).format('H[h]mm')
        },
    },
    props: ["block"],
    template: `
        <table class="main_table">
        <tr class="tr_header">
        <th class="th_date" @click="$emit('shownew', block.date + ' ')">{{ block.date }}</th>
        <th class="th_dayname" @click="$emit('shownew', block.date + ' ')"> {{ block.dayName }} </th>
        </tr>
        <tr class="tr_row" v-for="block in block.blocks" :key="block.key" @click="$emit('showmodify', block.id)">
            <td class="td_time" style="white-space:nowrap">{{ getTimeStartStr(block) }} - {{ getTimeStopStr(block) }}</td>
            <td class="td_activity">
                {{ block.activity }}
            </td>
        </tr>
        </table>
    `
})

new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        blocks: [],
        weekBlocks: [],
        showNewModal: false,
        showModifyModal: false,
        newText: '',
        idToDelete: null,
        log: '',
    },
    methods: {
        getShit () {
            axios
              .get('/tt/api/blocks/week')
              .then(response => (this.blocks = response.data))
              .catch(error => (alert("oops")));
        },
        addBlock: function () {
            axios.post('/tt/api/blocks/new', {'text': this.newText}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getShit()))
            .catch(error => this.printerr("status: " + error.response.status + "\n" + error.response.data))
            .then(() => {
                this.newText = '';
                this.showNewModal = false;
            });
        },
        deleteBlock: function () {
            axios.post('/tt/api/blocks/delete', {'pk': this.idToDelete}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getShit()))
            .catch(error => this.printerr())
            .then(() => {
                this.idToDelete = null;
                this.showModifyModal = false;
            });
        },
        test: function () {
            alert("a test ");
        },
        printerr: function (err_msg) {
            alert("ça a planté...\n\n" + err_msg);
        }
    },
    mounted() {
        this.getShit();
    }
})