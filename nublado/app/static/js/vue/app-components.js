const Tag = {
  mixins: [BaseTag]
}

const ToggleTag = {
  mixins: [BaseToggleTag]
}

const AjaxTag = {
  mixins: [BaseTag],
  props: {
    confirmId: {
      type: String,
      default: "delete-modal"
    },
    deleteUrl: {
      type: String,
      default: ""
    }
  },
  template: `
    <transition name="fade-transition" v-on:after-enter="isVisible = true" v-on:after-leave="remove">
    <div
    :id="id" 
    class="tag"
    v-bind:key="id"
    v-show="isVisible"
    >

      <a 
      @click.prevent="select"
      > 
      {{ value }} 
      </a>

      <ajax-delete
      v-if="hasRemove"
      :delete-confirm-id="confirmId"
      :delete-url="deleteUrl"
      @ajax-success="isVisible = false"
      inline-template
      >
        <a
        class="delete-btn"
        @click.prevent="confirmDelete"
        >
          &nbsp;
          <i class="fa-times fas"></i>
        </a>

      </ajax-delete>

    </div>
    </transition>
  `
}

const Tagbox = {
  mixins: [
    BaseTagbox,
    ClickOutsideMixin
  ],
  props: {
    repeatedTags: {
      type: Boolean,
      default: false
    },
    caseSensitive: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      tagInput: "",
    }
  },
  methods: {
    clearTagInput() {
      this.tagInput = ""
    },
    addTag(tag) {
      this.clearTagInput()

      if (!this.repeatedTags) {
        var repeatFound = false

        for (var i = 0; i < this.tags.length; i++) {
            if (this.tags.indexOf(tag) != -1) {
              repeatFound = true
              break
            }
        }

        if (!repeatFound) {
          this.$emit("add-tag", tag)
        }
      } else {

        this.$emit("add-tag", tag)
      }
    },
    removeTag(index) {
      this.clearTagInput()
      this.$emit("remove-tag", index)
    },
    selectTag(index) {
      this.clearTagInput()
      this.$emit("select-tag", index)
    },
    onClickOutside() {
      this.clearTagInput()
    }
  }
}

const MarkdownEditor = {
  mixins: [
    AjaxProcessMixin,
    MarkdownMixin
  ],
  props: {
    viewElementId: {
      type: String,
      default: "markdown-html-view"
    },
    initMarkdown: {
      type: String,
      default: ""
    },
    saveUrl: {
      type: String,
      default: ""
    },
    editorRows: {
      type: Number,
      default: 6
    },
    defaultModeEdit: {
      type: Boolean,
      default: true
    },
  },
  data() {
    return {
      markdown: this.initMarkdown,
      html: "",
      isEditing: false,
      saveTimerId: null
    }
  },
  methods: {
    edit() {
      this.isEditing = true
    },
    view() {
      if (this.isEditing) {
        this.save()
      }

      this.isEditing = false
      this.convertMarkdown()
    },
    save() {
      if (this.saveUrl) {
        this.process()
        this.convertMarkdown()

        this.saveTimerId = setTimeout(()=>{
          axios.put(this.saveUrl, {"content": this.markdown})
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
          .finally(() => {
            this.$emit("markdown-save")
          })
        }, 500)
      }
    },
    convertMarkdown() {
      this.html = this.markdownToHtml(this.markdown)
    }
  },
  created() {
    if (this.defaultModeEdit) {
      if (this.markdown) {
        this.convertMarkdown()
      }

      this.edit()
    } else {
      this.view()
    }
  },
  template: `
  <div class="markdown-editor">

  <div class="markdown-editor-controls">

  <div class="controls-left">

  <a 
  v-bind:class="['button', { 'is-info': !isEditing }]"
  :disabled="processing"
  href="#"
  @click.prevent="view"
  >
  <slot name="view-label">
  View
  </slot>
  </a>

  <a 
  v-bind:class="['button', { 'is-info': isEditing }]"
  :disabled="processing"
  href="#"
  @click.prevent="edit"
  >
  <slot name="edit-label">
  Edit
  </slot>
  </a>

  </div>

  <div class="controls-right">

  <a 
  v-bind:class="['button is-success', { 'is-loading': processing }]"
  href="#"
  @click.prevent="save"
  >
  <slot name="save-label">
  Save
  </slot>
  </a>

  </div>

  </div><!-- markdown-editor-controls -->

  <div 
  class="field"
  v-show="isEditing"
  >
  <div class="control">
  <textarea 
  class="textarea"
  :rows="editorRows"
  v-model="markdown"
  >
  </textarea>
  </div>
  </div>

  <div 
  class="box view-box"
  v-show="!isEditing"
  >

  <div
  :id="viewElementId" 
  class="view-text"
  v-html="html"
  >
  </div>

  </div>

  </div>
  `
}

const AjaxDelete = {
  mixins: [AjaxProcessMixin],
  props: {
    deleteConfirmId: {
      type: String,
      default: "confirmation-modal"
    },
    deleteUrl: {
      type: String,
      default: "",
    },
    deleteRedirectUrl: {
      type: String,
      default: ""
    },
    initTimerDelay: {
      type: Number,
      default: 500
    },
    initData: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    return {
      timerId: null,
      timerDelay: this.initTimerDelay,
      data: this.initData
    }
  },
  methods: {
    confirmDelete() {
      this.$modal.showConfirmation(this.deleteConfirmId)
      .then(yes => {
        console.log(yes)
        this.onDelete()
      })
      .catch(no => {
        console.log(no)
      })
    },
    onDelete(event) {
      this.success()
      this.process()
      clearTimeout(this.timerId)
      this.timerId = setTimeout(()=>{
        axios.delete(this.deleteUrl, {data:this.data})
        .then(response => {
          if (this.deleteRedirectUrl) {
            window.location.replace(this.deleteRedirectUrl)
          }
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
      }, this.timerDelay)
    }
  }
}

const AlertMessage = {
  mixins: [BaseMessage],
  template: `
    <transition name="fade-transition-slow" v-on:after-enter="isOpen = true" v-on:after-leave="isOpen = false">

    <div v-show="isOpen" :class="[messageType, "alert abs-alert"]">

    <div class="alert-content">
    {{ messageText }}
    </div>

    <a href=""
    type="button" 
    class="close"
    @click.prevent="close"
    >
    <span aria-hidden="true">&times;</span>
    </a>

    </div>

    </transition>
  `

}

const Dropdown = {
  mixins: [BaseDropdown],
  template: `
    <div 
    v-bind:id="id" 
    class="dropdown" 
    v-bind:class="[{ 'is-active': isOpen }, dropdownClasses]"
    >

    <div class="dropdown-trigger">
    <a 
    class="button" 
    href="#" 
    @click.prevent="toggle"
    >
    <slot name="dropdown-label">
    Dropdown
    </slot>
    </a>
    </div>

    <div class="dropdown-menu">
    <div class="dropdown-content">

    <div @click="toggle(false)">
    <slot name="dropdown-content">
    <div class="dropdown-item">
    Dropdown content
    </div>
    </slot>
    </div>

    </div>
    </div>

    </div>
  `  
}

const NavbarDropdown = {
  mixins: [Dropdown],
  template: `
    <div 
    v-bind:id="id" 
    class="navbar-item has-dropdown" 
    v-bind:class="[{ 'is-active': isOpen }, dropdownClasses]"
    >

    <a class="navbar-link" @click.prevent="toggle">

    <slot name="dropdown-label">
    Dropdown
    </slot>

    </a>

    <div class="navbar-dropdown is-right">

    <slot name="dropdown-content">
      Put something here, ideally a list of menu items.
    </slot>

    </div>   

    </div>
  `  
}

const FileUploader = {
  mixins: [BaseFileUploader]
}

const AudioFileUploader = {
  mixins: [BaseFileUploader],
  methods: {
    validateFile() {
      validated = false

      if (this.file.type == "audio/mpeg") {
        validated = true
      } else {
        console.error("Invalid file type")
      }
      
      return validated
    }
  }
}

const convertTimeHHMMSS = (val) => {
  let hhmmss = new Date(val * 1000).toISOString().substr(11, 8)

  return hhmmss.indexOf("00:") === 0 ? hhmmss.substr(3) : hhmmss
}

const Modal = {
  mixins: [BaseModal],
  created() {
    ModalPlugin.EventBus.$on(this.modalId, () => {
      this.show()
    })
  },
}

const ConfirmationModal = {
  mixins: [BaseModal],
  data() {
    return {
      yes: null,
      no: null
    }
  },
  methods: {
    confirm() {
      this.yes("yes")
      this.isOpen = false
    },
    close() {
      this.no("no")
      this.isOpen = false
    }
  },
  created() {
    ModalPlugin.EventBus.$on(this.modalId, (resolve, reject) => {
      this.show()
      this.yes = resolve
      this.no = reject
    })
  }
}

// AUDIO PLAYER 

const AudioPlayer = {
  props: {
    audioPlayerId: {
      type: String,
      default: "audio-player"
    },
    autoPlay: {
      type: Boolean,
      default: false
    },
    initLoop: {
      type: Boolean,
      default: false
    },
    hasLoopBtn: {
      type: Boolean,
      default: true
    },
    hasStopBtn: {
      type: Boolean,
      default: true
    },
    hasMuteBtn: {
      type: Boolean,
      default: true
    },
    hasDownloadBtn: {
      type: Boolean,
      default: true
    },
    hasVolumeBtn: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      audio: null,
      seekBar: null,
      playing: false,
      resumePlaying: false, // after mouseup
      dragging: false,
      loading: false,
      currentSeconds: 0,
      durationSeconds: 0,
      loop: false,
      showVolume: false,
      previousVolume: 35,
      volume: 100,
      hasError: false,
    }
  },
  computed: {
    currentTime() {
      return convertTimeHHMMSS(this.currentSeconds)
    },
    durationTime() {
      return convertTimeHHMMSS(this.durationSeconds)
    },
    percentComplete() {
      return parseInt(this.currentSeconds / this.durationSeconds * 100)
    },
    muted() {
      return this.volume / 100 === 0
    }
  },
  watch: {
    playing(value) {
      if (value) {
        this.playAudio()
      } else {
        this.pauseAudio()
      }
    },
    volume(value) {
      this.showVolume = false
      this.audio.volume = this.volume / 100
    }
  },
  methods: {
    playAudio() {
      this.audio.play()
    },
    pauseAudio() {
      this.audio.pause()
    },
    download() {
      if (this.audio.src) {
        this.stop()
        window.location.assign(this.audio.src)
      }
    },
    load() {
      if (this.audio.readyState >= 2) {
        console.log("audio loaded")
        this.loading = false
        this.durationSeconds = parseInt(this.audio.duration)

        if (this.autoPlay) {
          this.audio.play()
        }
      } else {
        throw new Error("Failed to load sound file.")
      }
    },
    mute() {
      if (this.muted) {
        return this.volume = this.previousVolume
      }

      this.previousVolume = this.volume
      this.volume = 0
    },
    seek(e) {
      this.playing = false

      const el = this.seekBar.getBoundingClientRect()
      const seekPos = (e.clientX - el.left) / el.width

      this.audio.currentTime = parseInt(this.audio.duration * seekPos)
    },
    stop() {
      this.playing = false
      this.audio.currentTime = 0
    },
    update() {
      this.currentSeconds = parseInt(this.audio.currentTime)
    },
    error() {
      this.hasError = true
      console.error("Error loading audio")
    },
    onProgressMousedown(e) {
      if (!this.loading) {
        this.dragging = true
        this.resumePlaying = this.playing
      }
    },
    onProgressMouseup(e) {
      if (this.dragging) {
        this.dragging = false
        this.seek(e)

        if (this.resumePlaying && !this.playing) {
          this.playing = true
        }
      }
    },
    onProgressMousemove(e) {
      if (this.dragging) {
        this.seek(e)
      }
    }
  },
  created() {
    this.loop = this.initLoop
  },
  mounted() {
    this.audio = this.$el.querySelector("#" + this.audioPlayerId)
    this.audio.addEventListener("error", this.error)
    this.audio.addEventListener("play", () => { this.playing = true })
    this.audio.addEventListener("pause", () => { this.playing = false });
    this.audio.addEventListener("ended", this.stop)
    this.audio.addEventListener("timeupdate", this.update)
    this.audio.addEventListener("loadeddata", this.load)
    this.seekBar = this.$el.querySelector("#" + this.audioPlayerId + "-seekbar")

    window.addEventListener("mouseup", this.onProgressMouseup)
    window.addEventListener("mousemove", this.onProgressMousemove)
  },
}