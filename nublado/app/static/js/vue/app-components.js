const EditComponent = {
  props: {
    initCanEdit: {
      type: Boolean,
      default: false
    },
  },
  data() {
    return {
      canEdit: this.initCanEdit
    }
  },
}

const AjaxDelete = {
  mixins: [AjaxProcessMixin],
  props: {
    confirmationId: {
      type: String,
      default: 'confirmation-modal'
    },
    deleteUrl: {
      type: String,
      default: '',
    },
    redirectUrl: {
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
      this.$modal.showConfirmation(this.confirmationId)
      .then(yes => {
        console.log(yes)
        this.onSubmit()
      })
      .catch(no => {
        console.log(no)
      })
    },
    onSubmit(event) {
      this.process()
      clearTimeout(this.timerId)
      this.timerId = setTimeout(()=>{
        axios.post(this.deleteUrl)
        .then(response => {
          if (this.redirectUrl) {
            window.location.replace(this.redirectUrl)
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
    this.audio.addEventListener('ended', () => { this.playing = false })
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
  mixins: [BaseToggleTag]
}

const DeleteTag = {
  mixins: [BaseDeleteTag]
}
