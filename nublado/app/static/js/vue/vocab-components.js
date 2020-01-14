const VocabSource = {
  mixins: [
    AdminMixin,
    VisibleMixin,
    MarkdownMixin
  ],
  props: {
    id: {
      type: String,
      default: ""
    },
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
      viewUrl: "",
      editUrl: "",
      deleteUrl: ""
    }
  },
  methods: {
    view() {
      if (this.viewUrl) {
        window.location.replace(this.viewUrl)
      }
    },
    edit() {
      if (this.editUrl) {
        window.location.replace(this.editUrl)
      }
    },
    remove() {
      this.$emit("delete-vocab-source")
    },
  },
  created() {
    if (this.initViewUrl) {
      this.viewUrl = this.initViewUrl
        .replace(0, this.source.id)
        .replace("zzz", this.source.slug)   
    }

    if (this.initEditUrl) {
      this.editUrl = this.initEditUrl
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
    id: {
      type: String,
      default: ""
    },
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
    sourceId: {
      type: String,
      default: null
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
    id: {
      type: String,
      default: ""
    },
    initVocabEntry: {
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
      vocabEntry: this.initVocabEntry,
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
      this.$emit("delete-vocab-entry", this.vocabEntry.id)
    },
  },
  created() {
    if (this.initViewUrl) {
      this.viewUrl = this.initViewUrl
        .replace("xx", this.vocabEntry.language)
        .replace("zzz", this.vocabEntry.slug)
    }

    if (this.initDeleteUrl) {
      this.deleteUrl = this.initDeleteUrl
        .replace(0, this.vocabEntry.id)
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

const VocabEntrySearch = {
  mixins: [BaseLanguageSearch],
  methods: {
    setResult(result) {
      this.searchTerm = result
      this.search()
    },
    search(val) {
      clearTimeout(this.searchTimerId)
      this.isOpen = false
      url = this.searchUrl + "?search_entry=" + encodeURIComponent(this.searchTerm) + "&search_language=" + this.language
      window.location.replace(url);
    }
  },
}

const VocabEntryTagSearch = {
  mixins: [BaseLanguageSearch],
  methods: {
    setResult(result) {
      this.searchTerm = result
      this.search()
    },
    search() {
      clearTimeout(this.searchTimerId)
      this.isOpen = false
      var tag = {
        language: this.language,
        entry: this.searchTerm
      }
      this.searchTerm = ""
      this.$emit("search", tag)
    }
  },
}

const VocabEntryTagbox = {
  components: {
    VocabEntryTagSearch
  },
  mixins: [BaseTagbox],
  methods: {
    addTag(tag) {
      /*
      tag: Object with language and entry properties
      */
      if (tag.entry) {
        const vocabEntryTag = {
          language: tag.language,
          value: tag.entry
        }
        this.$emit("add-tag", vocabEntryTag)
      }
    }
  }
}

const VocabEntryInstanceTagbox = {
  mixins: [Tagbox],
  methods: {
  }
}

const VocabEntryInfo = {
  mixins: [AjaxProcessMixin],
  props: {
    endpointUrl: {
      type: String,
      required: true
    },
  },
  data() {
    return {
      vocabEntryInfo: {},
      vocabEntryInfoVisible: false,
      vocabEntryInfoLoaded: false,
      hasError: false
    }
  },
  methods: {
    toggleVocabEntryInfoVisible() {
      this.vocabEntryInfoVisible = !this.vocabEntryInfoVisible
      
      if (this.vocabEntryInfoVisible && !this.vocabEntryInfoLoaded) {
        this.getVocabEntryInfo()
      }
    },
    getVocabEntryInfo() {
      this.process()
      axios.get(
        this.endpointUrl
      )
      .then(response => {
        this.vocabEntryInfo = response.data;
        this.vocabEntryInfoLoaded = true
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
        console.error("VocabEntryInfo error")
        this.hasError = true
      })
      .finally(() => this.complete())
    }
  }
}

const VocabEntryRandom = {
  mixins: [AjaxProcessMixin],
  props: {
    endpointUrl: {
      type: String,
      required: true
    },
    initViewUrl: {
      type: String,
      default: ""
    },
  },
  data() {
    return {
      vocabEntry: {},
      vocabEntryLoaded: false,
      viewUrl: "",
      hasError: false,
      timerId: null,
      timerDelay: 500,
    }
  },
  methods: {
    viewEntry() {
      if (this.initViewUrl) {
        this.viewUrl = this.initViewUrl
        .replace("xx", this.vocabEntry.language)
        .replace("zzz", this.vocabEntry.slug)  
        window.location.replace(this.viewUrl)
      }
    },
    getVocabEntry() {
      clearTimeout(this.timerId)
      this.vocabEntryLoaded = false
      this.process()

      this.timerId = setTimeout(()=>{
        axios.get(
          this.endpointUrl
        )
        .then(response => {
          this.vocabEntry = response.data;
          this.vocabEntryLoaded = true
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
          console.error("VocabEntry error")
          this.hasError = true
        })
        .finally(() => this.complete())
      }, this.timerDelay)
    }
  },
  created() {
    this.getVocabEntry()
  }
}


const VocabContext = {
  mixins: [
    MarkdownMixin,
    HighlightMixin,
    VisibleMixin,
    AdminMixin
  ],
  props: {
    id: {
      type: String,
      default: ""
    },    
    initVocabContext: {
      type: Object,
      required: true
    },
    initVocabSourceUrl: {
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
      vocabContext: this.initVocabContext,
      vocabSourceUrl: this.initVocabSourceUrl,
      editUrl: this.initDeleteUrl,
      deleteUrl: this.initDeleteUrl
    }
  },
  methods: {
    selectVocabSource() {
      if (this.vocabSourceUrl) {
        window.location.replace(this.vocabSourceUrl)
      }
    },
    edit() {
      if (this.editUrl) {
        window.location.replace(this.editUrl)
      }
    },
    remove() {
      this.$emit("delete-vocab-context")
    },
  },
  created() {

    if (this.initVocabSourceUrl) {
      this.vocabSourceUrl = this.initVocabSourceUrl
        .replace(0, this.vocabContext.vocab_source_id)
        .replace('zzz', this.vocabContext.vocab_source_slug)
    }

    if (this.initEditUrl) {
      this.editUrl = this.initEditUrl
        .replace(0, this.vocabContext.id)
    }
  
    if (this.initDeleteUrl) {
      this.deleteUrl = this.initDeleteUrl
        .replace(0, this.vocabContext.id)
    }
  }
}

const VocabContextTags = {
  mixins: [VocabContext],
  props: {
    initVocabEntries: {
      type: Array,
      default: []
    },
    initTagSelectUrl: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      vocabEntries: [],
      selectedVocabEntry: null,
      tagSelectUrl: this.initTagSelectUrl
    }
  },
  methods: {
    selectTag(index) {
      this.selectedVocabEntry = this.vocabEntries[index]

      if (this.tagSelectUrl) {
        this.tagSelectUrl = this.tagSelectUrl
          .replace("xx", this.selectedVocabEntry.language)
          .replace("zzz", this.selectedVocabEntry.slug)
        window.location.replace(this.tagSelectUrl)
      }
    },
    toggleTag(index) {
      if (this.selectedVocabEntry == null) {
        this.selectedVocabEntry = this.vocabEntries[index]
        this.selectedVocabEntry.selected = true
        this.highlight(this.selectedVocabEntry.tags)
      } else if (this.selectedVocabEntry.id != this.vocabEntries[index].id) {
        this.selectedVocabEntry.selected = false
        this.clearHighlight()
        this.selectedVocabEntry = this.vocabEntries[index]
        this.selectedVocabEntry.selected = true
        this.highlight(this.selectedVocabEntry.tags)
      } else {
        this.selectedVocabEntry.selected = !this.selectedVocabEntry.selected

        if (this.selectedVocabEntry.selected) {
          this.highlight(this.selectedVocabEntry.tags)
        } else {
          this.clearHighlight()
        }
      }
    },
    loadEntries() {
      for (var k in this.initVocabEntries) {
        const initVocabEntry = this.initVocabEntries[k]["vocab_entry"]
        const initTags = this.initVocabEntries[k]["tags"]
        const vocabEntry = {
          id: initVocabEntry.id,
          value: initVocabEntry.entry,
          slug: initVocabEntry.slug,
          language: initVocabEntry.language,
          selected: false,
          tags: initTags
        }
        this.vocabEntries.push(vocabEntry)
      }
    },
  },
  created() {
    this.loadEntries()
  }
}

const VocabEntryContext = {
  /**
  From many-to-many VocabContextEntry that refers to VocabEntry and VocabContext objects
  in Django
  **/
  mixins: [
    MarkdownMixin,
    HighlightMixin,
    VisibleMixin,
    AdminMixin
  ],
  props: {
    id: {
      type: String,
      default: ""
    },    
    initVocabEntryContext: {
      type: Object,
      required: true
    },
    initVocabSourceUrl: {
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
      vocabEntryContext: this.initVocabEntryContext,
      vocabSourceUrl: this.initVocabSourceUrl,
      editUrl: this.initEditUrl,
      deleteUrl: this.initDeleteUrl
    }
  },
  methods: {
    selectVocabSource() {
      if (this.vocabSourceUrl) {
        window.location.replace(this.vocabSourceUrl)
      }
    },
    edit() {
      if (this.editUrl) {
        window.location.replace(this.editUrl)
      }
    },
    remove() {
      this.$emit("delete-vocab-context")
    },
  },
  created() {
    console.log(this.vocabEntryContext)

    this.$nextTick(() => {
      this.highlight(this.vocabEntryContext.vocab_entry_tags)
    })

    if (this.initVocabSourceUrl) {
      this.vocabSourceUrl = this.initVocabSourceUrl
        .replace(0, this.vocabEntryContext.vocab_source_id)
        .replace('zzz', this.vocabEntryContext.vocab_source_slug)
    }

    if (this.initEditUrl) {
      this.editUrl = this.initEditUrl
        .replace(0, this.vocabEntryContext.vocab_context_id)
    }
  
    if (this.initDeleteUrl) {
      this.deleteUrl = this.initDeleteUrl
        .replace(0, this.vocabEntryContext.vocab_context_id)
    }
  }
}

const VocabContexts = {
  mixins: [
    AjaxProcessMixin,
    PaginationMixin,
    AdminMixin
  ],
  props: {
    vocabContextsUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      vocabContexts: null
    }
  },
  methods: {
    getVocabContexts(page=1) {
      this.process()

      params = {
        page: page
      }

      axios.get(this.vocabContextsUrl, {
        params: params
      })
      .then(response => {
        this.vocabContexts = response.data.results
        this.setPagination(
          response.data.previous,
          response.data.next,
          response.data.page_num,
          response.data.count,
          response.data.num_pages
        )
        VueScrollTo.scrollTo({
          el: '#vocab-contexts-scroll-top',
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
    onDeleteVocabContext(index) {
      this.$delete(this.vocabContexts, index)
    }
  },
  created() {
    this.getVocabContexts()
  }
}

const VocabEntryContexts = {
  mixins: [VocabContexts]
}

const VocabContextEditor = {
  /**
  Quick note: In this component, VocabEntry refers to the base vocab entry,
  and VocabEntryInstance refers to the usages of said VocabEntry in the context.
  **/
  components: {
    "markdown-editor": MarkdownEditor
  },
  mixins: [
    HighlightMixin
  ],
  props: {
    initVocabEntries: {
      type: Array,
      default: () => ([])
    },
    vocabEntryDetailUrl: {
      type: String,
      required: true
    },
    addVocabEntryUrl: {
      type: String,
      required: true
    },
    removeVocabEntryUrl: {
      type: String,
      required: true
    },
    addVocabEntryInstanceUrl: {
      type: String,
      required: true
    },
    removeVocabEntryInstanceUrl: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      vocabEntries: [],
      selectedVocabEntry: null
    }
  },
  methods: {
    selectVocabEntry(index) {
      this.selectedVocabEntry = this.vocabEntries[index]
      this.clearHighlight()
      this.highlight(this.selectedVocabEntry.tags)
    },
    deselectVocabEntry() {
      console.log("deselect")
      this.clearHighlight()
      this.selectedVocabEntry = null
    },
    addVocabEntry(tag) {
      /*
      tag: Object with value and language properties
      */
      params = {language: tag.language, entry: tag.value}

      axios.get(this.vocabEntryDetailUrl, {
        params: params
      })
      .then(response => {
        console.log("Vocab entry verified.")

        const data = response.data
        const vocabEntryId = data.id

        const vocabEntry = {
          id: vocabEntryId,
          value: data.entry,
          language: data.language,
          tags: []
        }

        axios.post(this.addVocabEntryUrl, {"vocab_entry_id": vocabEntryId})
        .then(response => {
          console.log("Vocab entry added.")
          this.vocabEntries.push(vocabEntry)
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
        .finally(() => {})
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
      .finally(() => {})    
    },
    removeVocabEntry(index) {
      const vocabEntry = this.vocabEntries[index]

      axios.post(this.removeVocabEntryUrl, {"vocab_entry_id": vocabEntry.id})
      .then(response => {
        console.log("Vocab entry deleted.")
        this.$delete(this.vocabEntries, index)
        this.deselectVocabEntry()
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
      .finally(() => {})      
    },
    addVocabEntryInstance(tag) {
      const vocabEntryInstance = {
        "vocab_entry_id": this.selectedVocabEntry.id,
        "vocab_entry_tag": tag
      }

      axios.post(this.addVocabEntryInstanceUrl, vocabEntryInstance)
      .then(response => {
        console.log("Vocab entry instance added.")
        this.selectedVocabEntry.tags.push(tag)
        this.highlight(this.selectedVocabEntry.tags)
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
      .finally(() => {})
    },
    removeVocabEntryInstance(index) {
      const tag = this.selectedVocabEntry.tags[index]

      const vocabEntryInstance = {
        "vocab_entry_id": this.selectedVocabEntry.id,
        "vocab_entry_tag": tag
      }

      axios.post(this.removeVocabEntryInstanceUrl, vocabEntryInstance)
      .then(response => {
        this.$delete(this.selectedVocabEntry.tags, index)
        this.clearHighlight()
        this.highlight(this.selectedVocabEntry.tags)
        console.log("Vocab entry instance " + tag + " removed.")
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
      .finally(() => {})      
    },
    loadVocabEntries() {
      for (var i in this.initVocabEntries) {
        const initVocabEntry = this.initVocabEntries[i]["vocab_entry"]
        const initTags = this.initVocabEntries[i]["tags"]

        const vocabEntry = {
          id: initVocabEntry.id,
          value: initVocabEntry.entry,
          language: initVocabEntry.language,
          tags: initTags
        }
        this.vocabEntries.push(vocabEntry)
      }
    },
    onMarkdownSave() {
      if (this.selectedVocabEntry) {
        this.clearHighlight()
        this.highlight(this.selectedVocabEntry.tags)
      }
      
      console.log("onMarkdownSave")
    }
  },
  created() {
    this.loadVocabEntries()
  }
}