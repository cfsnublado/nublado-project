const ModalPlugin = {

  install(Vue, options) {
    this.EventBus = new Vue()

    Vue.prototype.$modal = {
      show(modalId='modal') {
        ModalPlugin.EventBus.$emit(modalId)
      },

      showConfirmation(modalId='confirmation-modal') {
        let promise = new Promise((resolve, reject) => {
          ModalPlugin.EventBus.$emit(modalId, resolve, reject)
        })
        return promise
      }
    }
  }
}