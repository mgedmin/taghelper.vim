" File: taghelper.vim
" Author: Marius Gedminas <marius@gedmin.as>
" Version: 0.3.2
" Last Modified: 2020-11-05

augroup TagHelper
  autocmd!
  if exists(":pyx") && (has("python") || has("python3"))
    autocmd CursorMoved * call taghelper#cursormoved()
    autocmd CursorMovedI * call taghelper#cursormoved()
    autocmd BufDelete * silent call taghelper#bufdeleted()
  endif
augroup END
