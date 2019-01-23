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
    },
    methods: {
        getShit () {
            axios
              .get('/tt/api/blocks/week')
              .then(response => (this.blocks = response.data));
        },
        getTimeStartStr(block) {
            return moment(block.time_start).format('H[h]mm')
        },
        getTimeStopStr(block) {
            return moment(block.time_end).format('H[h]mm')
        },
        addBlock: function () {
            axios.post('/tt/api/blocks/new', {'text': this.newText}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getShit()));
            this.newText = '';
            this.showNewModal = false;
        },
        deleteBlock: function () {
            axios.post('/tt/api/blocks/delete', {'pk': this.idToDelete}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getShit()));
            this.idToDelete = null;
            this.showModifyModal = false;
        },
        test: function () {
            alert("a test ");
        }
    },
    mounted() {
        this.getShit();
    }
})