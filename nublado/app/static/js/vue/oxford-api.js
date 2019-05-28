/** THIRD PARTY **/

const OxfordApi = {
  mixins: [AjaxProcessMixin],
  props: {
    initEndpointUrl: {
      type: String,
      required: true
    },
    initEntry: {
      type: String,
      required: true
    },
    initLanguage: {
      type: String,
      default: 'en'
    },
    initEnglishRegion: {
      type: String,
      default: 'us'
    }
  },
  data() {
    return {
      endpointUrl: this.initEndpointUrl,
      entry: this.initEntry,
      language: this.initLanguage,
      region: this.initEnglishRegion
    }
  },
  methods: {
    searchApi() {
      axios.get(
        this.endpointUrl, {
          params: {
            language: this.language,
            entry: this.entry,
            region: this.region
          }
        }
      )
      .then(response => {
        this.success()
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
    }
  }
}