" File: chelper.vim
" Author: Marius Gedminas <marius@gedmin.as>
" Version: 0.1.0
" Last Modified: 2019-08-07

augroup TagHelper
  autocmd!
  if has("python") || has("python3")
    pyx import taghelper
    autocmd CursorMoved * call taghelper#cursormoved()
    autocmd CursorMovedI * call taghelper#cursormoved()
    autocmd BufDelete * silent call taghelper#bufdeleted()
  endif
augroup END
