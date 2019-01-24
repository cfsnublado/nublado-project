
// Instantiate components
Vue.component('ajax-delete', AjaxDelete)
Vue.component('alert-message', AlertMessage)
Vue.component('dropdown', Dropdown)
Vue.component('modal', Modal)
Vue.component('confirmation-modal', ConfirmationModal)
Vue.component('source-search', SourceSearch)
Vue.component('entry-search', EntrySearch)
Vue.component('entry-form', EntryForm)
Vue.component('context-form', ContextForm)
Vue.component('project-form', ProjectForm)
Vue.component('context-tagger', ContextTagger)
Vue.component('entry-tag-search', EntryTagSearch)
Vue.component('entry-tagbox', EntryTagbox)
Vue.component('entry-instance-tagbox', EntryInstanceTagbox)
Vue.component('entry-toggle-tag', EntryToggleTag)
Vue.component('context-tag-panel', ContextTagPanel)
Vue.component('tag', Tag)
Vue.component('toggle-tag', ToggleTag)
Vue.component('delete-tag', DeleteTag)
Vue.component('symbol-key', SymbolKey)
Vue.component('ipa-symbol-key', IpaSymbolKey)
Vue.component('symbol-keypad', SymbolKeypad)
Vue.component('ipa-symbol-keypad', IpaSymbolKeypad)
Vue.component('entry-definitions', EntryDefinitions)
Vue.component('vocab-entries', VocabEntries)
Vue.use(ModalPlugin)

Vue.filter('capitalize', function (value) {
  if (!value) return ''
  value = value.toString()
  return value.charAt(0).toUpperCase() + value.slice(1)
})

// Instantiate main app instance.
const vm = new Vue({
  el: '#app-container',
  delimiters: ['[[', ']]'],
  data: {
    showSidebar: sidebarExpanded,
    sidebarSessionEnabled: initSidebarSessionEnabled,
    sidebarOpenClass: 'sidebar-nav-expanded',
    sidebarPanelOpenClass: 'sidebar-nav-top-panel-expanded',
    appSessionUrl: appSessionUrl,
    windowWidth: 0,
    windowWidthSmall: 640,
    windowResizeTimer: null,
  },
  computed: {
    smallWindow: function() {
      return this.windowWidth <= this.windowWidthSmall
    }
  },
  methods: {
    showModal(modalId) {
      this.$modal.show(modalId)

      //  Close sidebar if modal opened from sidebar in small view.
      if (this.smallWindow && this.showSidebar) {
        this.toggleSidebar(false)
      }
    },
    toggleSidebar(manual) {
      // If manual is set to true or false, override toggle.
      if (manual === true || manual === false) {
        this.showSidebar = manual
      } else {
        this.showSidebar = !this.showSidebar
      }
  
      if (this.showSidebar) {
        document.body.classList.add(this.sidebarOpenClass)
      } else {
        document.body.classList.remove(this.sidebarOpenClass)
      }

      if (this.sidebarSessionEnabled) {
        this.setSidebarSession()
      }
    },
    toggleSidebarPanel() {
      // Hacky.
      const el = this.$refs.sidebarNav
      if (el.classList.contains(this.sidebarPanelOpenClass)) {
        el.classList.remove(this.sidebarPanelOpenClass)
      } else {
        el.classList.add(this.sidebarPanelOpenClass)
      }
    },
    setSidebarSession(disableLock = false) {
      var locked = disableLock ? false : this.showSidebar
      axios.post(this.appSessionUrl, {
        session_data: {
          "sidebar_locked": locked
        }
      })
      .then(response => {
        console.log(response)
      })
      .catch(error => {
        console.log(error)
      })
    },
    windowResize() {
      // Fire event after window resize completes.
      clearTimeout(this.windowResizeTimer)
      this.windowResizeTimer = setTimeout(()=>{
        this.windowWidth = document.documentElement.clientWidth
        if (this.smallWindow) {
          console.log('small')
          if (this.sidebarSessionEnabled) {
            this.setSidebarSession(true)
            this.sidebarSessionEnabled = false
          }
        } else {
          this.sidebarSessionEnabled = initSidebarSessionEnabled
          if (this.sidebarSessionEnabled) {
            this.setSidebarSession()
          }
        }
      }, 250);
    }
  },
  mounted() {
    this.$nextTick(function() {
      window.addEventListener('resize', this.windowResize);
      this.windowResize()
    })
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.windowResize);
  }
})