" File: chelper.vim
" Author: Marius Gedminas <marius@gedmin.as>
" Version: 0.1.2
" Last Modified: 2019-08-13

augroup TagHelper
  autocmd!
  if exists(":pyx") && (has("python") || has("python3"))
    pyx import taghelper
    autocmd CursorMoved * call taghelper#cursormoved()
    autocmd CursorMovedI * call taghelper#cursormoved()
    autocmd BufDelete * silent call taghelper#bufdeleted()
  endif
augroup END
