
const AjaxDelete = {
  mixins: [AjaxProcessMixin],
  props: {
    deleteConfirmId: {
      type: String,
      default: 'confirmation-modal'
    },
    deleteUrl: {
      type: String,
      default: '',
    },
    deleteRedirectUrl: {
      type: String,
      default: ''
    },
    initTimerDelay: {
      type: Number,
      default: 500
    }
  },
  data() {
    return {
      timerId: null,
      timerDelay: this.initTimerDelay,
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
      this.process()
      clearTimeout(this.timerId)
      this.timerId = setTimeout(()=>{
        axios.delete(this.deleteUrl)
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
  mixins: [BaseMessage]
}

const Dropdown = {
  mixins: [BaseDropdown]
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
      this.yes('yes')
      this.isOpen = false
    },
    close() {
      this.no('no')
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

const AudioPlayer = {
  props: {
    initAudioId: {
      type: String,
      required: true
    },
    initSoundFile: {
      type: String,
      default: null
    }
  },
  data() {
    return {
      audioId: this.initAudioId,
      soundFile: this.initSoundFile,
      audio: null,
      playing: false,
      loaded: false
    }
  },
  methods: {
    load() {
      if(this.audio.readyState >= 2) {
        this.loaded = true

        return this.playing = false
      }

      throw new Error('Failed to load sound file.')
    },
    stop() {
      this.playing = false
      this.audio.currentTime = 0
    },
  },
  watch: {
    playing(value) {
      if(value) {
        return this.audio.play()
      }
    }
  },
  mounted() {
    this.audio = this.$el.querySelector('#' + this.audioId)
    this.audio.addEventListener('loadeddata', this.load)
    this.audio.addEventListener('play', () => { this.playing = true })
    this.audio.addEventListener('ended', () => { this.stop() })
  },
  template: `
    <span>
      <a @click.prevent="playing = !playing" href="#"> <i class="vocab-pronunciation-icon fas fa-volume-up"></i> </a>
      <audio :id="audioId" ref="audiofile" :src="soundFile" preload="auto" style="display: none;"></audio>
    </span>
  `
}

const Tag = {
  mixins: [BaseTag]
}

const ToggleTag = {
  mixins: [ BaseToggleTag ]
}

const AjaxTag = {
  mixins: [BaseTag],
  props: {
    initConfirmId: {
      type: String,
      default: 'delete-modal'
    },
    initDeleteUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      confirmId: this.initConfirmId,
      deleteUrl: this.initDeleteUrl
    }
  },
  template: `
    <transition name="fade-transition" v-on:after-enter="isVisible = true" v-on:after-leave="isVisible = false">
    <div 
    class="ui label tagblock"
    v-bind:key="id"
    v-show="isVisible"
    >
      <a 
      class="tag-text"
      @click.prevent="select"
      > 
      {{ value }} 
      </a>

      &nbsp;

      <ajax-delete
      v-if="canRemove"
      :delete-confirm-id="confirmId"
      :delete-url="deleteUrl"
      @ajax-success="remove"
      inline-template
      >
        <a
        @click.prevent="confirmDelete"
        >
          <i class="fa-times fas"></i>
        </a>
      </ajax-delete>

    </div>
    </transition>
  `
}
