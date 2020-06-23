const DbxFile = {
  mixins: [
    AdminMixin,
    VisibleMixin,
  ],
  props: {
    initFile: {
      type: Object,
      required: true
    },
    initDeleteUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      file: this.initFile,
      deleteUrl: this.initDeleteUrl
    }
  },
  methods: {
    selectDbxFile(file) {
      this.$emit('select-dbx-file', file)
    },
    remove() {
      this.$emit('delete-dbx-file', this.file.id)
    }
  },
}

const DbxUserFiles = {
  components: {
    'dbx-file': DbxFile
  },
  mixins: [
    AdminMixin,
    AjaxProcessMixin
  ],
  props: {
    filesUrl: {
      type: String,
      required: true
    },
  },
  data() {
    return {
      files: null,
    }
  },
  methods: {
    getFiles() {
      this.files = []
      this.process()
      
      axios.get(this.filesUrl)
      .then(response => {
        this.files = response.data.files
        console.log(this.files)
      })
      .catch(error => {
        if (error.response) {
          console.error(error.response)
        } else if (error.request) {
          console.error(error.request)
        } else {
          console.error(error.message)
        }
        console.error(error.config)
      })
      .finally(() => {
        this.complete()
      })
    },
    selectDbxFile(path) {
      this.$emit('select-dbx-file', path)
    },
    onDeleteDbxFile(index) {
      this.$delete(this.files, index)
      this.$emit('delete-dbx-file')
    }
  },
  computed: {
    sortedFiles: function() {
      // If files array isn't null and has elements, sort it by filename.
      if (this.files && this.files.length > 0) {
        return this.files.sort(function(a, b) {
          var textA = a.name.toUpperCase()
          var textB = b.name.toUpperCase()
          return (textA < textB) ? -1 : (textA > textB) ? 1 : 0
        })
      } else {
        return this.files
      }
    }
  },
}

const DbxAudioFileUploader = {
  mixins: [
    AudioFileUploader
  ],
  data() {
    return {
      fileMetadata: ''
    }
  },
  methods: {
    success(response) {
      this.clear()
      this.fileMetadata = response.data['file_metadata']
      this.$emit('upload-dbx-file', this.fileMetadata)
    },
    clear() {
      this.file = null
    },
    sortFilesByName() {

    }
  },
  template: `
    <div>
    
    <div class="file has-name is-fullwidth">

    <label class="file-label">

    <input 
    class="file-input" 
    type="file" 
    ref="file" 
    name="resume"
    @change="handleFileUpload"
    :disabled="processing"
    >

    <span class="file-cta">

    <span class="file-icon">
    <i class="fas fa-upload"></i>
    </span>

    <span class="file-label">
    <slot name="label-select-file">
    Choose a file
    </slot>
    </span>

    </span>

    <span class="file-name"><span v-if="file" ref="filename">{{ file.name }}</span></span>

    </label>

    <button 
    class="button is-primary"
    v-bind:class="[{ 'is-loading': processing }]"
    @click.prevent="submitFile"
    :disabled="file == ''"
    >

    <slot name="label-submit">
    Submit
    </slot>
    
    </button>

    </div>

    </div>
  `
}

const Dbx = {
  mixins: [
    AdminMixin,
    AjaxProcessMixin
  ],
  components: {
    'dbx-user-files': DbxUserFiles,
    'dbx-audio-file-uploader': DbxAudioFileUploader,
  },
  props: {
    sharedLinkUrl: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      processing: false,
      sharedLink: ''
    }
  },
  methods: {
    getSharedLink(dbxPath) {
      this.processing = true
      
      axios.post(
        this.sharedLinkUrl,
        {'dbx_path': dbxPath}
      )
      .then(response => {
        if (response.data['shared_link']) {
          this.sharedLink = response.data['shared_link'].replace('dl=0', 'dl=1')
        }
      })
      .catch(error => {
        if (error.response) {
          console.error(error.response)
        } else if (error.request) {
          console.error(error.request)
        } else {
          console.error(error)
        }
        console.error(error.config)
      })
      .finally(() => {
        this.processing = false
      })
    },
    onChangeDbxFile() {
      this.sharedLink = ''
    },
    onUploadDbxFile(dbxPath) {
      this.getSharedLink(dbxPath)
      this.$refs['dbx-user-files'].getFiles()
    },
    onDeleteDbxFile() {
      this.sharedLink = ''
      this.$refs['dbx-audio-file-uploader'].clear()
    }
  }
}