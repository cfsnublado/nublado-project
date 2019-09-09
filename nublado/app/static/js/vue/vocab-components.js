const VocabSource = {
  mixins: [
    AdminMixin,
    VisibleMixin,
    MarkdownMixin
  ],
  props: {
    initSource: {
      type: Object,
      required: true
    },
    initViewUrl: {
      type: String,
      default: ""
    },
    initEditUrl: {
      type: String,
      default: ""
    },
    initDeleteUrl: {
      type: String,
      default: ""
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
      this.$emit("delete-vocab-source", this.project.id)
    }
  },
  created() {
    if (this.initViewUrl) {
      this.viewUrl = this.initViewUrl
        .replace(0, this.source.id)
        .replace("zzz", this.source.slug)   
    }

    if (this.initDeleteUrl) {
      this.deleteUrl = this.initDeleteUrl
        .replace(0, this.source.id)
    } 
  }
}

const VocabSources = {
  components: {
    "vocab-source": VocabSource
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
      vocabSources: null
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
          el: "#vocab-sources-scroll-top",
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
  mixins: [
    BaseSearch
  ],
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

const VocabSourceEntrySearch = {
  mixins: [BaseLanguageSearch],
  props: {
    initSourceId: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      sourceId: this.initSourceId,
    }
  },
  methods: {
    setResult(result) {
      this.searchTerm = result
      this.search()
    },
    search(val) {
      clearTimeout(this.searchTimerId)
      this.isOpen = false
      url = this.searchUrl + "?search_entry=" + encodeURIComponent(this.searchTerm) + "&search_language=" + this.language + "&search_source=" + this.sourceId
      window.location.replace(url);
    }
  },
}

const VocabEntry = {
  mixins: [
    AdminMixin,
    VisibleMixin
  ],
  props: {
    initEntry: {
      type: Object,
      required: true
    },
    initViewUrl: {
      type: String,
      default: ""
    },
    initEditUrl: {
      type: String,
      default: ""
    },
    initDeleteUrl: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      entry: this.initEntry,
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
      this.$emit("delete-vocab-entry", this.entry.id)
    }
  },
  created() {
    if (this.initViewUrl) {
      this.viewUrl = this.initViewUrl
        .replace("xx", this.entry.language)
        .replace("zzz", this.entry.slug)
    }

    if (this.initDeleteUrl) {
      this.deleteUrl = this.initDeleteUrl
        .replace(0, this.entry.id)
    }
  }
}

const VocabEntries = {
  components: {
    "vocab-entry": VocabEntry
  },
  mixins: [
    AjaxProcessMixin,
    AdminMixin,
    PaginationMixin,
  ],
  props: {
    initLanguage: {
      type: String,
      default: "en"
    },
    vocabEntriesUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      language: this.initLanguage,
      vocabEntries: null
    }
  },
  methods: {
    getVocabEntries(page=1) {
      this.process()

      params = {
        language: this.language,
        page: page
      }

      axios.get(this.vocabEntriesUrl, {
        params: params
      })
      .then(response => {
        this.vocabEntries = response.data.results
        this.setPagination(
          response.data.previous,
          response.data.next,
          response.data.page_num,
          response.data.count,
          response.data.num_pages
        )
        VueScrollTo.scrollTo({
          el: "#vocab-entries-scroll-top",
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
    setLanguage(language) {
      this.language = language
      this.getVocabEntries()
    },
    onDeleteVocabEntry(index) {
      this.$delete(this.vocabEntries, index)
    }
  },
  created() {
    this.getVocabEntries()
  }
}