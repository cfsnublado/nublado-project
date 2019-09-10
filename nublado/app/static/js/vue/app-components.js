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

const AjaxTag = {
  mixins: [BaseTag],
  props: {
    initConfirmId: {
      type: String,
      default: "delete-modal"
    },
    initDeleteUrl: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      confirmId: this.initConfirmId,
      deleteUrl: this.initDeleteUrl
    }
  },
  template: `
    <transition name="fade-transition" v-on:after-enter="isVisible = true" v-on:after-leave="remove">
    <div 
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
      v-if="canRemove"
      :delete-confirm-id="confirmId"
      :delete-url="deleteUrl"
      @ajax-success="isVisible = false"
      inline-template
      >
        <a
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

const AlertMessage = {
  mixins: [BaseMessage],
  template: `
    <transition name="fade-transition-slow" v-on:after-enter="isOpen = true" v-on:after-leave="isOpen = false">

    <div v-show="isOpen" :class="[messageType, 'alert abs-alert']">

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