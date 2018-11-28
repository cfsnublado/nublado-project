const OxfordApi = {
  props: {
    initEndpointUrl: {
      type: String,
      required: true
    },
    initEnglishRegion: {
      type: String,
      default: 'us'
    }
  },
  data() {
    return {
      endpointUrl: this.initEndpointUrl,
      language: 'en',
      entry: '',
      processing: false,
    }
  },
  methods: {

    searchApi() {
      axios.get(
        this.endpointUrl, {
          params: {
            language: this.language,
            entry: this.entry
          }
        }
      )
      .then(response => {
        this.success(response)
      })
      .catch(error => {
        if (error.response) {
          console.log(error.response)
        } else if (error.request) {
          console.log(error.request)
        } else {
          console.log(error.message)
        }
        console.log(error.config)
      })
      .finally(() => this.complete())
    },
    process() {
      this.processing = true
      this.$emit('ajax-process')
    },
    complete() {
      this.processing = false
      this.$emit('ajax-complete')
    },
    success(response) {
      console.log(response)
      this.$emit('ajax-success')
    }, 
  }

}