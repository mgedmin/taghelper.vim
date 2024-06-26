function taghelper#curtag()
  if exists("w:TagHelperCurTag")
    return w:TagHelperCurTag
  else
    return ""
  endif
endfunction

function taghelper#cursormoved()
  if !exists('b:current_syntax') || b:current_syntax !~ '^\(c\|cpp\|python\|diff\|javascript\|cfg\|dosini\|robot\|help\)\(\.\|$\)'
    let w:TagHelperCurTag = ''
    return
  endif
  pyx import taghelper
  let w:TagHelperCurTag = pyxeval('taghelper.findtag()')
endfunction

function taghelper#bufdeleted()
  let w:TagHelperCurTag = ""
  pyx import taghelper
  exec 'pyx taghelper.deltags(' . expand("<abuf>") . ')'
endfunction

function taghelper#checkpython()
  if !has("python") && !has("python3")
    echoerr "taghelper.vim needs Python support"
    return 0
  endif
  if !exists(":pyx")
    echoerr "taghelper.vim needs vim 8.0.0251 or neovim 0.4.0"
    return 0
  endif
  return 1
endfunction

function taghelper#showtags()
  if !taghelper#checkpython()
    return
  endif
  pyx import taghelper
  exec 'pyx taghelper.showtags(' . bufnr("") . ', ' . b:changedtick . ')'
endfunction

function taghelper#reimport()
  if !taghelper#checkpython()
    return
  endif
  pyx import importlib, sys, taghelper
  pyx [importlib.reload(v) for k, v in list(sys.modules.items()) if k.startswith('taghelper_')]
  pyx importlib.reload(taghelper)
endfunction
