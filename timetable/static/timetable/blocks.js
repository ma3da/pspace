Vue.component('modal', {
    template: '#modal-template',
    data: function () {
        return {
          text: ''
        };
    },
    methods: {
        close: function () {
            this.$emit('close');
            this.text = '';
        },
        addBlock: function () {
            axios.post('/tt/api/new', {'text': this.text}, {headers: {'X-CSRFToken': $cookies.get('csrftoken')}})
            .then(response => (this.getShit()));
            this.close()
        }
    }
})

new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        blocks: [],
        weekBlocks: [],
        showModal: false,
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
        }
    },
    mounted() {
        this.getShit();
    }
})