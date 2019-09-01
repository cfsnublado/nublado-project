const VocabSource = {
  mixins: [
    AdminMixin,
    VisibleMixin
  ],
  props: {
    initSource: {
      type: Object,
      required: true
    },
    initViewUrl: {
      type: String,
      default: ''
    },
    initEditUrl: {
      type: String,
      default: ''
    },
    initDeleteUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      source: this.initSource,
      viewUrl: this.initViewUrl,
      editUrl: this.initEditUrl,
      deleteUrl: this.initDeleteUrl
    }
  },
  methods: {
    view() {
      if (this.viewUrl) {
        window.location.replace(this.viewUrl)
      }
    },
    edit() {},
    remove() {
      this.$emit('delete-vocab-source', this.project.id)
    }
  },
  created() {
    if (this.initViewUrl) {
      this.viewUrl = this.initViewUrl
        .replace(0, this.source.id)
        .replace('zzz', this.source.slug)   
    }

    if (this.initDeleteUrl) {
      this.deleteUrl = this.initDeleteUrl
        .replace(0, this.source.id)
    } 
  }
}

const VocabSources = {
  components: {
    'vocab-source': VocabSource
  },
  mixins: [
    AdminMixin,
    AjaxProcessMixin,
    PaginationMixin,
  ],
  props: {
    vocabSourcesUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      vocabSources: []
    }
  },
  methods: {
    getVocabSources(page=1) {
      this.process()

      params = {
        page: page
      }

      axios.get(this.vocabSourcesUrl, {
        params: params
      })
      .then(response => {
        this.vocabSources = response.data.results
        this.setPagination(
          response.data.previous,
          response.data.next,
          response.data.page_num,
          response.data.count,
          response.data.num_pages
        )
        VueScrollTo.scrollTo({
          el: '#vocab-sources-scroll-top',
        })
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
      .finally(() => {
        this.complete()
      })
    },
    onDeleteVocabSource(index) {
      this.$delete(this.vocabSources, index)
    }
  },
  created() {
    this.getVocabSources()
  }
}

const VocabSourceSearch = {
  mixins: [BaseSearch],
  methods: {
    setResult(result) {
      this.searchTerm =result
      this.search()
    },
    search() {
      clearTimeout(this.searchTimerId)
      this.isOpen = false
      url = this.searchUrl + "?source=" + encodeURIComponent(this.searchTerm)
      window.location.replace(url)
    }
  }
}